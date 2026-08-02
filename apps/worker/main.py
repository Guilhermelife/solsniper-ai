from apps.worker.scout import scan_tokens
from apps.worker.analyzer import analyze_token


def run():

    print("🚀 SolSniper Worker iniciado")

    tokens = scan_tokens()

    print(
        f"Encontrados {len(tokens)} tokens"
    )

    for token in tokens[:5]:

        result = analyze_token(token)

        print("\n📊 Análise")
        print("====================")

        print(
            result
        )


if __name__ == "__main__":
    run()