from yoomoney import Authorize

Authorize(
    # Здесь изменять только client_id и redirect_uri
    client_id="",
    # client_secret указывать не нужно, если не ставили галочку "Проверять подлинность приложения (OAuth2 client_secret)" на этапе регистрации приложения
    client_secret="",
    # Ссылку указывать точно также, как в процессе регистрации приложения на сайте, они должны быть идентичны
    redirect_uri="https://t.me/example",
    scope=["account-info",
        "operation-history",
        "operation-details",
        "incoming-transfers",
        "payment-p2p",
        ]
)