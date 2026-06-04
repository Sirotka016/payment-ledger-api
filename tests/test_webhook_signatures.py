from app.core.signatures import build_payment_signature, verify_payment_signature


def test_payment_signature_matches_task_example():
    payload = {
        "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
        "user_id": 1,
        "account_id": 1,
        "amount": 100,
    }

    signature = build_payment_signature(
        payload,
        secret_key="gfdmhghif38yrf9ew0jkf32",
    )

    assert (
        signature == "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
    )


def test_payment_signature_verification_rejects_wrong_signature():
    payload = {
        "transaction_id": "external-transaction-id",
        "user_id": 1,
        "account_id": 1,
        "amount": 100,
    }

    assert verify_payment_signature(payload, "wrong-signature", "secret") is False


def test_payment_signature_does_not_use_signature_field():
    payload = {
        "transaction_id": "external-transaction-id",
        "user_id": 1,
        "account_id": 1,
        "amount": 100,
    }
    payload_with_signature = {
        **payload,
        "signature": "this-field-must-not-be-signed",
    }

    assert build_payment_signature(payload, "secret") == build_payment_signature(
        payload_with_signature,
        "secret",
    )
