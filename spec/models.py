from django.db import models
# from simple_history.models import HistoricalRecords


class Parameter(models.Model):
    param_str = models.CharField(unique=True, max_length=3)

    class Meta:
        db_table = "em_parameter"


class Report(models.Model):
    fpath = models.CharField()
    date_from = models.DateTimeField()
    date_to = models.DateTimeField()
    added = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "em_report"


class Trade(models.Model):
    mln = models.DecimalField(max_digits=16, decimal_places=9)
    is_long = models.BooleanField()
    open_price = models.DecimalField(max_digits=16, decimal_places=9)
    close_price = models.DecimalField(max_digits=16, decimal_places=9)
    pnl_curr = models.DecimalField(max_digits=16, decimal_places=9)
    pnl_pips = models.DecimalField(max_digits=16, decimal_places=9)
    open_dt = models.DateTimeField()
    close_dt = models.DateTimeField()
    tag = models.CharField()
    close_event = models.ForeignKey(
        to=Something
    )
    pnl = models.DecimalField(max_digits=16, decimal_places=9)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "em_trade"


class CloseEvent(models.Model):
    name = models.CharField()

    class Meta:
        db_table = "em_close_event"


class Instrument(models.Model):
    code = models.CharField()

    class Meta:
        db_table = "em_instrument"
