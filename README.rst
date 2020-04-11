=========================
django-pagseguro2-example
=========================

|Github Build Status|

----

Exemplo de projeto usando o django-pagseguro2.


Dependências para rodar o projeto
---------------------------------

* Python 3.8+
* Pipenv
* `Ngrok`_ (para receber as notificações do PagSeguro)

.. _`Ngrok`: https://ngrok.com/


Como rodar o projeto
--------------------

.. code:: shell

    pipenv install --dev
    cp local.env .env
    vim .env # edite as informações usando seus dados de sandbox do PagSeguro
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver 0.0.0.0:8000

Abra o navegador no endereço http://localhost:8000/admin/ para fazer login no sistema e criar os eventos e tickets.

Acesse o endereço http://localhost:8000/eventos/ para navegar pelos eventos e comprar os tickets.

Como receber notificações do PagSeguro
--------------------------------------

.. code:: shell

    ngrok http 8000

Anote o endereço do ngrok e atualize no `sandbox do PagSeguro`_

No sandbox, altere uma transação para o status pago e a notificação será enviada para o sistema. Ex: https://14742c67.ngrok.io/pagseguro/ (observe o '/' no final da url).

.. _`sandbox do PagSeguro`: https://sandbox.pagseguro.uol.com.br/vendedor/configuracoes.html


Como rodar os testes
--------------------

.. code:: shell

    pytest


Observações
-----------

* Todos os endereços /eventos/* são protegidos por login e senha, lembre-se de logar no admin antes de acessar.
* Apenas os status pago e cancelado que vem do PagSeguro foram mapeados nesse projeto.

.. |Github Build Status| image:: https://github.com/allisson/django-pagseguro2-example/workflows/tests/badge.svg
   :target: https://github.com/allisson/django-pagseguro2-example/actions
