from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from forms import TicketForm, ClienteForm
from datetime import datetime
import pytz
from models import db, Cliente, Ticket
from werkzeug.datastructures import ImmutableMultiDict

# Defina o fuso horário para Mato Grosso do Sul
# Ajuste para o fuso horário correto
timezone = pytz.timezone('America/Campo_Grande')


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tickets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'

db = SQLAlchemy(app)


class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    cnpj_cpf = db.Column(db.String(18), nullable=False, unique=True)
    razao_social = db.Column(db.String(100))
    telefone = db.Column(db.String(20), nullable=False)
    tickets = db.relationship('Ticket', backref='cliente', lazy=True)


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Aberto')
    data_abertura = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    cliente_id = db.Column(
        db.Integer, db.ForeignKey('cliente.id'), nullable=True)


@app.before_request
def before_request():
    if request.method == 'POST' and '_method' in request.form:
        method = request.form['_method'].upper()
        if method in ['PUT', 'DELETE']:
            request.environ['REQUEST_METHOD'] = method


@app.route('/')
def index():
    tickets_abertos = Ticket.query.filter_by(status='Aberto').count()
    tickets_finalizados = Ticket.query.filter_by(status='Finalizado').count()
    top_clientes = db.session.query(
        Cliente.nome, Cliente.email, db.func.count(
            Ticket.id).label('tickets_abertos')
    ).join(Ticket).filter(Ticket.status == 'Aberto').group_by(Cliente.id).order_by(db.func.count(Ticket.id).desc()).limit(5).all()
    return render_template('dashboard.html', abertos=tickets_abertos, finalizados=tickets_finalizados, top_clientes=top_clientes)


@app.route('/tickets')
def listar_tickets():
    tickets = Ticket.query.all()
    return render_template('listar_tickets.html', tickets=tickets)


@app.route('/tickets/novo', methods=['GET', 'POST'])
def criar_ticket():
    clientes = Cliente.query.all()
    form = TicketForm(clientes=[(cliente.id, cliente.nome)
                      for cliente in clientes])
    form_cliente = ClienteForm()

    if form.validate_on_submit():
        novo_ticket = Ticket(
            titulo=form.titulo.data,
            descricao=form.descricao.data,
            status=form.status.data,
            data_abertura=datetime.now(timezone),
            cliente_id=form.cliente_id.data or None
        )
        try:
            db.session.add(novo_ticket)
            db.session.commit()
            flash('Ticket criado com sucesso!', 'success')
            return redirect(url_for('listar_tickets'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar o ticket. Tente novamente. Erro: {
                  e}', 'danger')

    if form_cliente.validate_on_submit():
        novo_cliente = Cliente(
            nome=form_cliente.nome.data,
            email=form_cliente.email.data,
            cnpj_cpf=form_cliente.cnpj_cpf.data,
            razao_social=form_cliente.razao_social.data,
            telefone=form_cliente.telefone.data
        )
        try:
            db.session.add(novo_cliente)
            db.session.commit()
            flash('Cliente criado com sucesso!', 'success')
            # Recarregar a página para atualizar o dropdown
            return redirect(url_for('criar_ticket'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar o cliente. Tente novamente. Erro: {
                  e}', 'danger')

    return render_template('criar_ticket.html', form=form, form_cliente=form_cliente)


def coerce_to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@app.route('/tickets/editar/<int:ticket_id>', methods=['GET', 'POST'])
def editar_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    clientes = [(cliente.id, cliente.nome) for cliente in Cliente.query.all()]
    form = TicketForm(obj=ticket, clientes=clientes)

    if form.validate_on_submit():
        cliente_id = coerce_to_int(form.cliente_id.data)
        # Verifique o valor convertido
        print('Cliente ID convertido:', cliente_id)

        ticket.titulo = form.titulo.data
        ticket.descricao = form.descricao.data
        ticket.status = form.status.data
        ticket.cliente_id = cliente_id or None

        try:
            db.session.commit()
            flash('Ticket atualizado com sucesso!', 'success')
            return redirect(url_for('listar_tickets'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar o ticket. Tente novamente. Erro: {
                  e}', 'danger')

    print('Formulário inválido:', form.errors)
    return render_template('editar_ticket.html', form=form, ticket=ticket, clientes=clientes)


@app.route('/tickets/deletar/<int:ticket_id>', methods=['POST', 'DELETE'])
def deletar_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    flash('Ticket excluído com sucesso!', 'success')
    return redirect(url_for('listar_tickets'))


@app.route('/clientes/novo', methods=['POST'])
def criar_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        cliente = Cliente(
            nome=form.nome.data,
            email=form.email.data,
            cnpj_cpf=form.cnpj_cpf.data,
            razao_social=form.razao_social.data,
            telefone=form.telefone.data
        )
        db.session.add(cliente)
        db.session.commit()
        flash('Cliente criado com sucesso!', 'success')
    return redirect(url_for('listar_clientes'))


@app.route('/clientes/novo2', methods=['POST'])
def criar_cliente_ticket():
    form = ClienteForm()
    if form.validate_on_submit():
        cliente = Cliente(
            nome=form.nome.data,
            email=form.email.data,
            cnpj_cpf=form.cnpj_cpf.data,
            razao_social=form.razao_social.data,
            telefone=form.telefone.data
        )
        db.session.add(cliente)
        db.session.commit()
        flash('Cliente criado com sucesso!', 'success')
    return redirect(url_for('criar_ticket'))


@app.route('/editar_cliente/<int:cliente_id>', methods=['GET', 'POST'])
def editar_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    form = ClienteForm(obj=cliente)
    if form.validate_on_submit():
        form.populate_obj(cliente)
        db.session.commit()
        flash('Cliente atualizado com sucesso!', 'success')
        return redirect(url_for('listar_clientes'))
    return render_template('editar_cliente.html', form=form, cliente=cliente)


@app.route('/clientes/excluir/<int:cliente_id>', methods=['POST', 'DELETE'])
def excluir_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    db.session.delete(cliente)
    db.session.commit()
    flash('Cliente excluído com sucesso!', 'success')
    return redirect(url_for('listar_clientes'))


@app.route('/clientes', methods=['GET'])
def listar_clientes():
    clientes = Cliente.query.all()
    form = ClienteForm()  # Cria uma instância do formulário
    return render_template('clientes.html', clientes=clientes, form=form)


@app.route('/clientes/ids', methods=['GET'])
def listar_clientes_ids():
    clientes = Cliente.query.all()
    return '<br>'.join(f'ID:{cliente.id}, Nome: {cliente.nome}' for cliente in clientes)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
