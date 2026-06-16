export function renderErrorPage() {
  return `<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Erro</title>
    <style>
      body {
        margin: 0;
        min-height: 100vh;
        display: grid;
        place-items: center;
        font-family: Arial, sans-serif;
        background: #f8fafc;
        color: #0f172a;
      }
      main {
        max-width: 480px;
        padding: 32px;
        text-align: center;
      }
    </style>
  </head>
  <body>
    <main>
      <h1>Esta pagina nao carregou</h1>
      <p>Tente recarregar a pagina ou volte para o inicio.</p>
    </main>
  </body>
</html>`;
}
