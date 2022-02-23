import os

from context_broker.script_upload import delete_all, parse_json_ld


def main_example():
    delete_all()  # Clean slate.

    filename = os.path.join(os.path.dirname(__file__), 'examples/demo_context_broker.jsonld')
    parse_json_ld(filename, debug=True)

    if 0:
        r = post_example()
        try:
            print(r.status_code)
            print(r.content)
            print(r.json())
        except:
            pass

        r = delete_example()
        try:
            print(r.status_code)
            print(r.content)
            print(r.json())
        except:
            pass

    print('Script has finished.')


if __name__ == '__main__':
    main_example()
