# Valida apenas numero inteiro

def validar_inteiro(valor):

    try:

        return int(valor)

    except ValueError:

        print("\n❌ Valor inválido.")
        return None


# Valida o estoque, garantindo que seja um número inteiro não negativo

def validar_estoque(valor):

    try:

        estoque = int(valor)

        if estoque < 0:

            print("\n❌ Estoque não pode ser negativo.")
            return None

        return estoque

    except ValueError:

        print("\n❌ Estoque inválido.")
        return None

# Valida um texto vazio ou apenas com espaços em branco

def validar_texto(texto):

    if not texto.strip():

        return False

    return True

# Valida os status

def validar_status(status):

    status_validos = [

        "CONSISTENTE",
        "DIVERGENTE",
        "REVISAR"

    ]

    return status in status_validos