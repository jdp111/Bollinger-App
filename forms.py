from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, validators
from wtforms.validators import DataRequired, Email, Length

class SimulationForm(FlaskForm):
    """form for running simulation"""
    ticker = StringField('Ticker Symbol', validators = [DataRequired()])
    EMAres = IntegerField('EMA Resolution', validators = [DataRequired()])
    STDmult = FloatField('σ Multiplier', validators = [DataRequired()])