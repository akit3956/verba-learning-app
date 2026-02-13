import React, { useState, useEffect, useRef } from 'react';
import { BookOpen, Copy, Upload, Settings, RefreshCw, Image as ImageIcon, Download } from 'lucide-react';

const CATEGORIES = {
    reading: '読解テキスト生成',
    practice: '例文・例題作成',
    quiz: 'クイズ作成',
    vocab: '語彙リスト作成'
};

function MaterialGenerator() {
    const [category, setCategory] = useState('reading');
    const [level, setLevel] = useState('N4');
    const [topic, setTopic] = useState('');
    const [referenceText, setReferenceText] = useState('');

    // Config
    const [model, setModel] = useState('gemini-flash-latest');
    const [availableModels, setAvailableModels] = useState([]);
    const [showSettings, setShowSettings] = useState(false);

    // Results
    const [generatedContent, setGeneratedContent] = useState('');
    const [generatedImage, setGeneratedImage] = useState('');

    // States
    const [loading, setLoading] = useState(false);
    const [imageLoading, setImageLoading] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [fileName, setFileName] = useState('');

    const fileInputRef = useRef(null);

    // Initial Load
    useEffect(() => {
        loadModels();
    }, []);

    const loadModels = async () => {
        try {
            // Get Models
            const modelsResp = await fetch('http://localhost:8000/models');
            const modelData = await modelsResp.json();
            setAvailableModels(modelData.models || []);

            // Set default model if configured, else first available
            // Prefer gemini-flash-latest if available
            const hasGemini = modelData.models?.some(m => m.name === 'gemini-flash-latest');
            if (hasGemini) {
                setModel('gemini-flash-latest');
            } else if (modelData.models && modelData.models.length > 0) {
                // Fallback
                setModel(modelData.models[0].name);
            }
        } catch (e) {
            console.error("Init Error:", e);
        }
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        setFileName(`⌛ 解析中: ${file.name}`);
        setUploading(true);

        try {
            const res = await fetch('http://localhost:8000/api/materials/upload-reference', {
                method: 'POST',
                body: formData
            });

            if (!res.ok) throw new Error('Upload failed');
            const data = await res.json();

            setReferenceText(prev => (prev ? prev + "\n\n" : "") + data.extracted_text);
            setFileName(`✅ 完了: ${file.name}`);
            alert('ファイルを解析してテキストを取り込みました。');
        } catch (err) {
            console.error(err);
            alert("Upload Error: " + err.message);
            setFileName('❌ エラーが発生しました');
        } finally {
            setUploading(false);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    const handleGenerate = async () => {

        if (!topic) return alert("トピックを入力してください");
        setLoading(true);
        setGeneratedContent('');
        setGeneratedImage('');

        try {
            const res = await fetch('http://localhost:8000/api/materials/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ category, level, topic, model, reference_text: referenceText })
            });
            const data = await res.json();

            if (data.result) {
                setGeneratedContent(data.result);
            } else {
                throw new Error("Result empty");
            }
        } catch (e) {
            alert("Error: " + e.message);
        } finally {
            setLoading(false);
        }
    };

    const handleImageGenerate = async () => {
        if (!topic) return;
        setImageLoading(true);
        try {
            const res = await fetch('http://localhost:8000/api/materials/image', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: topic, model })
            });
            const data = await res.json();
            setGeneratedImage(data.image_url);
        } catch (e) {
            alert("Image Error: " + e.message);
        } finally {
            setImageLoading(false);
        }
    };

    const handleDownload = () => {
        const blob = new Blob([generatedContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `teaching_material_${category}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    };

    const formatContent = (text) => {
        if (!text) return { __html: '' };
        let html = text
            .replace(/([一-龠々ヶ々〇]+)[(（]([ぁ-んァ-ヶー]+)[)）]/g, '<ruby>$1<rt>$2</rt></ruby>')
            .replace(/\n/g, '<br>');
        return { __html: html };
    };

    return (
        <div style={{ paddingTop: '20px' }}>
            <div className="main-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h2>
                    <BookOpen style={{ display: 'inline', marginRight: 10, verticalAlign: 'middle' }} />
                    {CATEGORIES[category]}
                </h2>
                <div className="mode-selector" style={{ display: 'flex', gap: 10 }}>
                    {Object.entries(CATEGORIES).map(([key, label]) => (
                        <button
                            key={key}
                            className={`secondary-btn ${category === key ? 'active' : ''}`}
                            style={{
                                background: category === key ? 'var(--primary-color)' : 'white',
                                color: category === key ? 'white' : 'var(--text-main)',
                                borderColor: category === key ? 'var(--primary-color)' : '#d1d5db'
                            }}
                            onClick={() => setCategory(key)}
                        >
                            {label.split('作成')[0].split('生成')[0]} {/* Shorten label */}
                        </button>
                    ))}
                    <button className="secondary-btn" onClick={() => setShowSettings(!showSettings)}>
                        <Settings size={16} />
                    </button>
                </div>
            </div>

            {/* Settings Panel */}
            {showSettings && (
                <div className="admin-card" style={{ marginBottom: '2rem' }}>
                    <h3>Settings</h3>
                    <div className="input-group" style={{ marginBottom: '1rem' }}>
                        <label>AI Model</label>
                        <select value={model} onChange={(e) => setModel(e.target.value)}>
                            {availableModels.map(m => (
                                <option key={m.name} value={m.name}>
                                    {m.type === 'cloud' ? '☁️' : '🖥️'} {m.name} ({m.size})
                                </option>
                            ))}
                        </select>
                    </div>
                </div>
            )}

            <div className="controls">
                <div className="control-row">
                    <div className="input-group">
                        <label>Topic / Theme</label>
                        <input
                            type="text"
                            placeholder="Ex: Travel to Kyoto, Shopping, Grammar '〜tara'"
                            value={topic}
                            onChange={(e) => setTopic(e.target.value)}
                        />
                    </div>
                    <div className="input-group" style={{ flex: '0 0 150px' }}>
                        <label>Level</label>
                        <select value={level} onChange={(e) => setLevel(e.target.value)}>
                            {['N5', 'N4', 'N3', 'N2', 'N1'].map(l => <option key={l} value={l}>{l}</option>)}
                        </select>
                    </div>
                </div>

                <div className="input-group">
                    <label>Reference Material (Optional)</label>
                    <div className="file-upload-zone" onClick={() => fileInputRef.current.click()} style={{ cursor: 'pointer' }}>
                        <Upload size={16} />
                        <span className="file-name">{fileName || "Click to upload .pptx / .xlsx"}</span>
                        <input
                            type="file"
                            hidden
                            ref={fileInputRef}
                            onChange={handleFileUpload}
                            accept=".pptx,.xlsx"
                        />
                    </div>
                    <textarea
                        rows={3}
                        value={referenceText}
                        onChange={(e) => setReferenceText(e.target.value)}
                        placeholder="Paste text or upload file for context..."
                    />
                </div>
            </div>

            <div className="actions" style={{ justifyContent: 'center' }}>
                <button className="primary-btn" onClick={handleGenerate} disabled={loading} style={{ width: '200px' }}>
                    {loading ?
                        <span><RefreshCw className="spinner" style={{ width: 20, height: 20, display: 'inline', marginRight: 5 }} /> 生成中...</span>
                        : 'Generate'}
                </button>
            </div>

            {/* Results */}
            {(generatedContent || loading) && (
                <div style={{ marginTop: '2rem' }}>
                    {loading && <div id="loader" className="placeholder">Generating content... please wait.</div>}

                    {!loading && generatedContent && (
                        <>
                            <div className="actions" style={{ marginBottom: '1rem', marginTop: 0 }}>
                                <button className="secondary-btn" onClick={() => navigator.clipboard.writeText(generatedContent)}>
                                    <Copy size={16} style={{ marginRight: 5 }} /> Copy
                                </button>
                                <button className="secondary-btn" onClick={handleDownload}>
                                    <Download size={16} style={{ marginRight: 5 }} /> Save
                                </button>
                                <button className="secondary-btn" onClick={handleImageGenerate} disabled={imageLoading} style={{ background: '#ecfdf5', borderColor: '#10b981', color: '#047857' }}>
                                    {imageLoading ? '...' : <><ImageIcon size={16} style={{ marginRight: 5 }} /> Illustrate</>}
                                </button>
                            </div>

                            {generatedImage && (
                                <div className="image-area">
                                    <img src={generatedImage} alt="Generated" />
                                </div>
                            )}

                            <div
                                className="result-area"
                                dangerouslySetInnerHTML={formatContent(generatedContent)}
                            />
                        </>
                    )}
                </div>
            )}
        </div>
    );
}

export default MaterialGenerator;
