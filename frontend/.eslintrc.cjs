// ESLint 配置:React + TypeScript
// 用经典 .eslintrc.cjs(CJS)兼容 ESLint 8 + TypeScript(espree 不识别 TS,需 @typescript-eslint/parser)
module.exports = {
  root: true,
  env: { browser: true, es2022: true, node: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react/recommended',
    'plugin:react/jsx-runtime',
    'plugin:react-hooks/recommended',
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: { ecmaVersion: 'latest', sourceType: 'module' },
  settings: { react: { version: 'detect' } },
  plugins: ['react-refresh', '@typescript-eslint'],
  rules: {
    'react/prop-types': 'off', // TS 类型已保证
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
    '@typescript-eslint/no-explicit-any': 'warn', // 教学时难免 any,警告不阻断
    '@typescript-eslint/no-unused-vars': [
      'warn',
      { argsIgnorePattern: '^_' },
    ],
  },
  ignorePatterns: ['dist', '.eslintrc.cjs', 'node_modules'],
}
