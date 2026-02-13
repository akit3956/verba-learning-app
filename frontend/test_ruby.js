const logicSplit = (text) => {
    if (!text) return [];
    const parts = text.split(/([一-龠々ヶ々〇]+)[(（]([ぁ-んァ-ヶー]+)[)）]/g);
    const elements = [];
    for (let i = 0; i < parts.length; i += 3) {
        if (parts[i]) {
            elements.push(`TEXT[${parts[i]}]`);
        }
        if (i + 1 < parts.length && i + 2 < parts.length) {
            const kanji = parts[i + 1];
            const furigana = parts[i + 2];
            if (kanji && furigana) {
                elements.push(`RUBY[${kanji}|${furigana}]`);
            }
        }
    }
    return elements.join("");
};

const logicMatchAll = (text) => {
    if (!text) return [];
    // Regex for Kanji(Furigana)
    const regex = /([一-龠々ヶ々〇]+)[(（]([ぁ-んァ-ヶー]+)[)）]/g;

    let lastIndex = 0;
    const elements = [];

    let match;
    while ((match = regex.exec(text)) !== null) {
        // Text before match
        if (match.index > lastIndex) {
            elements.push(`TEXT[${text.substring(lastIndex, match.index)}]`);
        }

        // Match content
        const kanji = match[1];
        const furigana = match[2];
        elements.push(`RUBY[${kanji}|${furigana}]`);

        lastIndex = regex.lastIndex;
    }

    // Remaining text
    if (lastIndex < text.length) {
        elements.push(`TEXT[${text.substring(lastIndex)}]`);
    }

    return elements.join("");
};

const testCases = [
    "これはとてもおいしい___です。料理(りょうり)",
    "これでは「さ」をとって、「おいしさ」をします。「おいしさ」は「おいしい」です。文(ぶん)使(つか)表(ひょう)形容詞(けいようし)名詞形(めいしけい)他(ほか)選択肢(せんたくし)正(ただし)単(たん)",
    "普通のテキストのみ",
    "漢字(かんじ)のみ",
    "混在(こんざい)するパターン(ぱたーん)"
];

console.log("=== Testing Logic vs MatchAll ===\n");

testCases.forEach((text, i) => {
    console.log(`--- Case ${i + 1} ---`);
    console.log(`HasInput: ${text.substring(0, 30)}...`);
    console.log(`Current : ${logicSplit(text)}`);
    console.log(`Proposed: ${logicMatchAll(text)}`);
    console.log("");
});
