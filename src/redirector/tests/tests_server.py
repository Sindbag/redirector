from bottle import redirect, request, response, Bottle


app = Bottle()


@app.route('/status')
def status():
    return 'OK'


@app.route('/redirect/limitless')
def limitless_redirects():
    redirect("/redirect/limitless")


@app.route('/limitless_body')
def limitless_body():
    while 1:
        yield 'some_content\n'


@app.route('/redirect/to_limitless_body')
def redir_to_limitless_body():
    return redirect('/limitless_body')


@app.route('/redirect/limited/<number:int>')
def limited_redirects(number: int):
    if p := int(number):
        redirect(f'/redirect/limited/{p-1}')
    return 'Ok Response'


@app.route('/redirect/4k_body')
def redirect_big_body():
    response.status = 303
    response.set_header('Location', request.url)
    return 'some' * 1024


def run_server(**kwargs):
    from bottle import run
    run(app, **kwargs)


if __name__ == '__main__':
    run_server(host='localhost', port=8080, debug=True, quiet=True)