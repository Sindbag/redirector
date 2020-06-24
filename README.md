# Redirector
###### Тестовое задание

Необходимо написать программу на Python (рекомендуем использовать библиотеку requests), которая по заданному URL определяет URL, который не предполагает редиректов.
Программа должна учитывать:
- множественные редиректы;
- зацикленные редиректы;
- редиректы с бесконечным или достаточно большим телом ответа

Для тестирования программы необходимо написать тестовый сервер, который будет эмулировать указанные крайние случаи.

Также , пожалуйста, напишите свой фидбек о тестовом:
Он не должен быть очень большим. Нам интересно было бы узнать:
- Примерную оценку времени, которое вы потратили на выполнение задания;
- Комментарии по коду, почему выбран тот или иной способ решения;
- Возникали ли проблемы при выполнении тестового.

## How to install

`pip install .`

## How to run tests

`./run_tests.sh`

Starts `bottle` server in the background, runs tests against it, then kills server.

It was possible to monkeypatch requests.get used inside redirector by specific `pytest` functionality
and use `bottle` server answers as `fixtures` in order to have consistent runs,
instead of running server on loopback interface.

## Usage

```
from redirector import Redirector

redir = Redirector(max_redirects=30, content_limit=2 ** 33)
final_link = redir.resolve_redirects('http://localhost/redirected_link/')
```

Throws exceptions (all exceptions are inherited from `redirector.exceptions.RDException`):
- `RDTooManyRedirectsException` - when redirects count exceeds `max_redirects`;
- `RDTooBigBodyException` - when answer body exceeds `content_limit` (redir answer body is not fetched);
- `RDCycleRedirectsException` - when redirects are cycled.