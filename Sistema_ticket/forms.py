from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email


class ClienteForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    cnpj_cpf = StringField('CNPJ/CPF', validators=[DataRequired()])
    razao_social = StringField('Razão Social', validators=[DataRequired()])
    telefone = StringField('Telefone', validators=[DataRequired()])
    submit = SubmitField('Salvar Cliente')


class TicketForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired()])
    descricao = TextAreaField('Descrição', validators=[DataRequired()])
    status = SelectField('Status', choices=[
                         ('Aberto', 'Aberto'), ('Finalizado', 'Finalizado')])
    cliente_id = SelectField('Cliente', coerce=int)

    def __init__(self, *args, **kwargs):
        clientes = kwargs.pop('clientes', [])
        super(TicketForm, self).__init__(*args, **kwargs)
        self.cliente_id.choices = clientes
