module.exports = {
    env: {
        browser: true,
        es2015: true
    },
    extends: [
        "eslint:recommended",
        "plugin:vue/vue3-essential",
        "plugin:prettier/recommended",
        "@vue/typescript/recommended",
        "plugin:@typescript-eslint/recommended"
    ],
    parser: "vue-eslint-parser",
    parserOptions: {
        parser: "@typescript-eslint/parser",
        sourceType: "module",
        ecmaVersion: 2020,
        ecmaFeatures: {
            jsx: true
        }
    },
    plugins: ["vue"],
    rules: {
        "vue/multi-word-component-names": false
    }
}
