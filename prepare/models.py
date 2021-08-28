# File: models.py

from django.core.exceptions          import ValidationError
from django.core.validators          import MaxValueValidator, MinLengthValidator, MinValueValidator
from django.db                       import models
from django.db.models.constraints    import UniqueConstraint
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.db.models.fields         import AutoField, BooleanField, CharField, DateField, DateTimeField, IntegerField, TextField, URLField
from django.db.models.functions      import Random # For use in Fokusgruppe.rand_rank
from django.urls                     import reverse
from django.utils.translation        import gettext_lazy as _

import uuid


class Skole(models.Model):
    """Samle-struktur (klasse) for klasser. En lærer vil være tilknyttet (mindst 1) skole."""

    # Fields
    navn = models.CharField(max_length=100, help_text='Skolens officielle navn')
    kortnavn = models.CharField(max_length=20, help_text='Skolens korte navn')
    oprettet = models.DateTimeField(
        # auto_now_add=True VISER feltet i http://127.1:8000/admin/prepare/skole/
        #
        #default=datetime.now() #  
        auto_now_add=True, # https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.DateField.auto_now_add
    )
    opdateret = models.DateTimeField( # NB: Dato opdateres ved Model.save() ikke ved QuerySet.update(), se dokumenation!
        # auto_now=True SKJULER feltet i http://127.1:8000/admin/prepare/skole/, =False VISER feltet.
        #
        #default=datetime.now()#,
        auto_now=True, # https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.DateField.auto_now
    )

    # Metadata
    class Meta:
        ordering = ['navn']
        verbose_name_plural = 'skoler'

    # Methods
    def get_absolute_url(self):
        """Returnerer URL, der tilgår en bestemt instantiering af klassen Skole (en bestemt skole)."""
        return reverse('skole-detalje-visning', args=[str(self.id)])

    def __str__(self):
        """Streng, som repræsenterer Skole-objektet (på Admin siden etc.)."""
        return f"{self.kortnavn}: {self.navn}"


class Klasse(models.Model):
    """
    Skoleklasser, undervisningsgruppe eller hold. 
    Samler Elev-objekter.
    En lærer vil være tilknyttet (ingen eller flere) hold.
    """

    # Fields
    navn = models.CharField(max_length=100, help_text='Holdets administrative navn')
    kortnavn = models.CharField(max_length=20, help_text='Holdets  korte navn')
    oprettet = models.DateTimeField(
        #default=datetime.now() #  
        auto_now_add=True, # https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.DateField.auto_now_add
    )
    opdateret = models.DateTimeField( # NB: Dato odateres ved Model.save() ikke ved QuerySet.update(), se dokumenation!
        #default=datetime.now(), #
        auto_now=True, # https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.DateField.auto_now
    )
    skole = models.ForeignKey('Skole', on_delete=models.RESTRICT, null=True)
    startår = models.IntegerField(
        validators=[ MinValueValidator(1950), MaxValueValidator(2050)],
        help_text='Firecifret årstal for holdstart'
    )
    studieretning = CharField(
        max_length=3,
        choices=[
            ('stx', 'STX'),
            ('hf',  'HF'),
            ('htx', 'HTX'),
            ('hhx', 'HHX'),
            ('eux', 'EUX'),
            ('eud', 'EUD'),
            ('etc', 'Andet')
        ], 
        default='stx', 
        help_text='Klassens studieretning'
    )
    """Fortløbende nummerering af den runde/omgang af samplinger, https://trello.com/c/mDSvj2t2 , klassens elever sættes sammen i, i fokusgrupper """
    fokus_runde = models.IntegerField(
        validators=[ MinValueValidator(1), MaxValueValidator(999)],
        help_text='(automatisk) løbenummer for samplingsrunde til fokusgruppe'
    )
    """Antal medlemmer i fokusgruppe"""
    fokus_antal = models.IntegerField(
        validators=[ MinValueValidator(1), MaxValueValidator(35)], 
        default=5,
        help_text='Standardstørrelse af klassens fokusgruppe'
    )
    note = models.TextField(
        max_length=200, 
        blank=True,
        null=True,
        help_text='Lærerens generelle noter om holdet, dets lokale eller historik'
    )

    # Metadata
    class Meta:
        ordering = ['navn']
        verbose_name = 'klasse'
        verbose_name_plural = 'klasser'

    # Methods
    def get_absolute_url(self):
        """Returnerer URL, der tilgår en bestemt instantiering af klassen Klasse (et bestemt hold)."""
        return reverse('hold-detalje-visning', args=[str(self.id)])

    def __str__(self):
        """Streng, som repræsenterer Klasse-objektet (på Admin siden etc.)."""
        return f"{self.kortnavn} ({self.skole.kortnavn}): {self.navn}."


class Elev(models.Model):
    """
    Underviste personer. En lærer vil være tilknyttet (ingen eller flere) hold.
    Portrætbillede (foto) evt. i separat tabel/Model.
    """

    # Fields
    id = models.UUIDField( # https://stackoverflow.com/a/34264443/888033
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    oprettet = models.DateTimeField(
        auto_now_add=True, # https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.DateField.auto_now_add
    )
    opdateret = models.DateTimeField( # NB: Dato odateres ved Model.save() ikke ved QuerySet.update(), se dokumenation!
        auto_now=True,
    )
    fornavn = models.CharField(
        max_length=50, 
        validators=[MinLengthValidator(2)],
        help_text='Personens officielle fornavn(e) som i protokol'
    )
    efternavn = models.CharField(
        max_length=50, 
        validators=[MinLengthValidator(2)],
        help_text='Personens officielle efternavn(e) som i protokol'
    )
    kaldenavn = models.CharField(
        max_length=15, 
        null=True,
        blank=True,
        help_text='Det navn, personen ønsker brugt i daglig tiltale'
    )
    klasse = models.ForeignKey('Klasse', on_delete=models.RESTRICT, null=True)
    unilogin = models.CharField(
        max_length=8, 
        validators=[MinLengthValidator(8)],
        help_text='Personens officielle fornavn(e) som i protokol'
    )
    indmeldt = models.DateField(
        blank=True,
        null=True,
        help_text='Dato for hvornår eleven begynder at gå i klassen'
    )
    udmeldt = models.DateField(
        blank=True,
        null=True,
        help_text='Dato for hvornår eleven er holdt op med at gå i klassen'
    )
    mail = models.EmailField(help_text='Mail, læreren kan bruge til kommunikation med eleven')
    # https://stackoverflow.com/q/19130942/888033
    mobil = models.CharField(
        max_length=15, 
        validators=[MinLengthValidator(8)],
        help_text='Mobiltelefonnummer, system og lærer kan bruge til kommunikation med eleven'
    )
    note = models.TextField(
        max_length=200, 
        null=True,
        blank=True,
        help_text='Lærerens noter om eleven, elevens lokale eller historik. OBS der er mulighed andetsteds for løbende observationsnoter.'
    )

    class Meta:
        ordering = ['klasse', 'fornavn', 'efternavn']
        verbose_name_plural = 'elever'

    # Methods
    def get_absolute_url(self):
        """Returnerer URL, der tilgår en bestemt instantiering af klassen Klasse (et bestemt hold)."""
        return reverse('elev_detaljer', args=[str(self.id)])

    def __str__(self):
        """Streng, som repræsenterer Elev (på Admin siden etc.)."""
        return f"{self.fornavn} {self.efternavn} ({self.klasse.kortnavn})"


class FokusGruppe(models.Model):
    """
    Randomiseret liste over Elever. Gentagelser af samme Elev vil forekomme i længere forløb.
    En hel Klasse tilføjes ad gangen. 
    Rækkefølgen af Elever i Klassen skifter for hver `klasse.fokus_runde`, og bestemmes af `self.rand_rank`.
    Læreren tildeler sig til hvert Modul (hver "time") et antal elever fra klassen. Læreren giver hver elev i denne gruppe Adfærdsobservation.
    Reificerer relation mellem Elev og Modul.

    Sammenlagt FokusGruppe og Adfærd 1/8 2021
    """
    # Fields
    #elev_fg_runde_id = AutoField(primary_key=True, verbose_name='Fokusgruppens Elev-løbenummer')
    id = AutoField(primary_key=True, verbose_name='Fokusgruppe-kandidatens elev+modul-løbenummer')
    """Klasse (og dermed `Elev.Klasse.fokus_runde`), samt Elev gives af denne relation."""
    elev = models.ForeignKey('Elev', on_delete=models.RESTRICT, null=True)
    oprettet = models.DateTimeField(
        #default=timezone.now() 
        auto_now_add=True, # https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.DateField.auto_now_add
    )
    opdateret = models.DateTimeField( # NB: Dato odateres ved Model.save() ikke ved QuerySet.update(), se dokumenation!
        #default=timezone.now(), 
        auto_now=True, # https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.DateField.auto_now
    )
    """
        Modul udfyldes ikke ved generering af del-liste, 
        først når læreren udvælger hvor mange, der skal observeres i det pågældende Modul.
        Dato (og tid) gives af denne relation.
    """
    """
        Modul giver Forløb og knytter Elev til modulets fokusgruppe, når tildelt.
        Eleven i en instantiering (række) præsenteres i liste over Fokusgruppe-kandidater,
        hvis bedømt=False eller =Null. Sættes til =True, når observation registreres.
    """
    modul = models.ForeignKey(
        'Modul', 
        models.SET_NULL,
        blank=True, 
        null=True, 
    )

    #@property eller overflødig?
    bedømt = models.BooleanField(null=True, default='')

    """True, hvis Elev var til stede i Modul? Null indtil Elev er bedømt"""
    tilstede = BooleanField(null=True, default='')
    
    """
        Tilfældig værdi mellem 0 og 1, der tildeles ved oprettelse.
        Sorteringsværdi (indenfor Elev.Klasse.fokus_runde). 
    """
    rand_rank = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        # https://docs.djangoproject.com/en/3.2/ref/models/database-functions/#random
        # maybe also: https://realpython.com/python-random/
        default=Random(), # Introduced in Django 3.2
        editable=False,
        null=False
    )
    """
    De to sociale performance indicators er intenderet til at stimulere/måle elevernes 'Decency Quotient'. 
    Den faglige er til at stimulere/måle 'Intelligenskvitient'.
    Scores kan alene registreres (not Null), hvis `tilstede`=True (observation ikke mulig af fraværende elever).
    """
    def get_max_score():
        return 4
    spørg    = IntegerField(blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(get_max_score())], help_text='Score for elevens evne til at søge hjælp på fagligt spørgsmål')
    hjælp    = IntegerField(blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(4)], help_text='Score for elevens evne til at yde hjælp til faglig problemløsning')
    faglig   = IntegerField(blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(4)], help_text='Score for elevens evne til at bidrage til en faglig samtale')
    stikord  = CharField(   blank=True, null=True, max_length=30, help_text='Lærerens observationer i "tre" ord')
    reaktion = CharField(   blank=True, null=True, max_length=30, help_text='Elevens bemærkning')

    class Meta:
        ordering = ['id', 'elev']
        verbose_name = 'fokusgruppe til adfærdsobservation'
        verbose_name_plural = 'fokusgrupper til adfærdsobservation'
        # Suggested by @bdbd https://stackoverflow.com/q/68872046/888033
        # https://docs.djangoproject.com/en/3.2/ref/models/constraints/#uniqueconstraint
        constraints = [UniqueConstraint(fields=['elev', 'modul'], name='unik_modul_elev')]
 
    # Methods
    """Giver 'baglæns' URL-kodning mening for denne Model?"""
    def get_absolute_url(self):
        """Returnerer URL, der tilgår en bestemt instantiering af klassen Klasse (et bestemt hold)."""
        return reverse('fokusgruppe', args=[str(self.id)])

    def __str__(self):
        """Streng, som repræsenterer Elev (på Admin siden etc.)."""
        tmp_forløb = tmp_modul = '-'
        if self.modul:
            tmp_forløb = self.modul.forløb.titel
            if self.modul.afholdt:
                tmp_modul = self.modul.afholdt
            else:
                tmp_modul = 'NA'
            self.modul.forløb.titel
            return f"{self.elev.fornavn} {self.elev.efternavn}, d. {tmp_modul} om '{tmp_forløb}' (runde {self.klasse.fokus_runde} i {self.klasse.kortnavn})"
        else:
            tmp_forløb = 'Ukendt'
        return f"{self.elev.fornavn} {self.elev.efternavn} ikke tildelt (runde {self.klasse.fokus_runde} i {self.klasse.kortnavn})"
    
    @property # Getter method - avoiding reduncant data entry
    # Frit efter https://www.geeksforgeeks.org/python-property-decorator-property/
    def runde(self):
        """Runde af observation, fra Elev.Klasse.fokus_runde (redundant)."""
        return self.elev.klasse.fokus_runde
    @property
    def klasse(self):
        return self.elev.klasse
    
    #def clean(self,modul):
        """
            https://docs.djangoproject.com/en/3.2/ref/models/instances/#django.db.models.Model.clean
        """
    #    if( modul.forløb.klasse == self.klasse ):
    #        if FokusGruppe.elev in [fg.elev for fg in FokusGruppe.objects.filter(modul=FokusGruppe.modul)]:
    #            self.modul = modul
    #        else:
    #            raise( ValidationError(_(f'Modul {modul} har allerede fået tildelt Elev "{self.elev}".')) )
    #    else:
    #        raise( ValidationError(_('Klasse angivet af modul (gennem forløb) stemmer ikke med klasse angivet af elev.')) )

class Emne(models.Model):
    """Faglige emner, som danner rammen om forløb for de enkelte klasser"""
    id = AutoField(primary_key=True, verbose_name='Emne-løbenummer (automatisk)')
    titel = CharField(max_length=20, help_text='Betegnelse for emnet')
    oprettet = models.DateTimeField(
        #default=timezone.now() 
        auto_now_add=True, # https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.DateField.auto_now_add
    )
    opdateret = models.DateTimeField( # NB: Dato odateres ved Model.save() ikke ved QuerySet.update(), se dokumenation!
        #default=timezone.now(), #
        auto_now=True, # https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.DateField.auto_now
    )
    fag = CharField( # Eller ForeignKey til (ikke oprettet) Model: Fag.
        max_length=3,
        choices=[
            ('mat', 'Matematik'), 
            ('it',  'Informationsteknologi')
        ], 
        default='Matematik'
    )
    studieretning = CharField(
        max_length=3,
        choices=[
            ('stx', 'STX'),
            ('hf',  'HF'),
            ('htx', 'HTX'),
            ('hhx', 'HHX'),
            ('eux', 'EUX'),
            ('eud', 'EUD'),
            ('etc', 'Andet')
        ], 
        default='stx', 
        help_text='Klassens studieretning'
    )
    faglige_mål = TextField(max_length=1000, help_text='Bekendtgørelsens og skolens faggruppes krav til emnet')
    note = TextField(
        max_length=1000, 
        null=True,
        blank=True,
        help_text='Lærerens krav til og ambitioner for emnet'
    )
    klassetrin = IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        help_text='Årgang, emnet undervises på (siden holdets startår)',
    )
    varighed = IntegerField(help_text='Forventet antal lektioner/moduler')

    class Meta:
        ordering = ['fag', 'studieretning', 'klassetrin', 'titel']
        verbose_name_plural = 'emner'
    
    def __str__(self):
        return f"{self.fag}-{self.studieretning}/{self.klassetrin}: {self.titel}. "

    def get_absolute_url(self):
        """Returnerer URL, der tilgår en bestemt instantiering af Emne."""
        return reverse('emne-detalje-visning', args=[str(self.id)])


class Forløb(models.Model):
    """Forløb er et Emne, der gennemgås i en Klasse fra et bestemt tidspunkt (`påbegyndt`) og som har en planlagt `varighed`."""
    id = AutoField(primary_key=True, verbose_name='Forløbs-løbenummer (automatisk)')
    emne   = ForeignKey('Emne',   on_delete=models.RESTRICT, null=True)
    klasse = ForeignKey('Klasse', on_delete=models.RESTRICT, null=True)
    oprettet = models.DateTimeField(
        #default=timezone.now() 
        auto_now_add=True, # https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.DateField.auto_now_add
    )
    opdateret = models.DateTimeField( # NB: Dato odateres ved Model.save() ikke ved QuerySet.update(), se dokumenation!
        #default=timezone.now(), 
        auto_now=True, # https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.DateField.auto_now
    )
    titel = CharField(max_length=20, help_text='Overskrift for forløbet')
    påbegyndt = DateField(help_text='Dato for planlagt start af forløbet')
    varighed = IntegerField(help_text='Forventet antal lektioner/moduler')
    kommentar = TextField(
        max_length=500, 
        null=True,
        blank=True,
        help_text='Præsentation til holdets elever af det konkrete forløb i klassen'
    )

    class Meta:
        ordering = ['klasse', 'emne']
        verbose_name_plural = 'forløb'

    def __str__(self):
        return f"{self.klasse.kortnavn}: fra {self.påbegyndt} -- {self.emne}"
    
    def get_absolute_url(self):
        """Returnerer URL, der tilgår et bestemt Forløb."""
        return reverse('forloeb-detalje-visning', args=[str(self.id)])


class Modul(models.Model):
    """
        Modul er en 'time' eller lektion, der er/bliver `afholdt` på en bestemt dag som del af et Forløb.
    """
    id = AutoField(primary_key=True,verbose_name='Modul-løbenummer (automatisk)')
    forløb = ForeignKey('Forløb', on_delete=models.RESTRICT, null=True)
    oprettet = models.DateTimeField(
        #default=timezone.now() 
        auto_now_add=True, # https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.DateField.auto_now_add
    )
    opdateret = models.DateTimeField( # NB: Dato odateres ved Model.save() ikke ved QuerySet.update(), se dokumenation!
        #default=timezone.now(), 
        auto_now=True, # https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.DateField.auto_now
    )
    afholdt = DateField(help_text='Planlagt / faktisk dato for modulet')
    
    class Meta:
        ordering = ['afholdt', 'id']
        verbose_name_plural='moduler'

    def __str__(self):
        return f"Modul {self.id} '{self.forløb.titel}', {self.afholdt} ({self.forløb.klasse})."

    def get_absolute_url(self):
        """Returnerer URL, der tilgår et bestemt Modul."""
        return reverse('modul_tildel', args=[str(self.id)])


class Video(models.Model):
    """
       Præsentation på video (eller i personligt fremmøde) af opgave stillet 
       i forbindelse med et Forløb.
       https://trello.com/c/ZReTY2UN
    """
    id = AutoField(primary_key=True,verbose_name='Løbenummer (automatisk) for videopræsentation')
    forløb = ForeignKey('Forløb', on_delete=models.RESTRICT, null=False)
    elev   = ForeignKey('Elev',   on_delete=models.RESTRICT, null=False)
    oprettet = models.DateTimeField(
        #default=timezone.now() 
        auto_now_add=True, # https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.DateField.auto_now_add
    )
    opdateret = models.DateTimeField( # NB: Dato odateres ved Model.save() ikke ved QuerySet.update(), se dokumenation!
        #default=timezone.now(), 
        auto_now=True, # https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.DateField.auto_now
    )
    """
        Valideres til at ligge efter `forløb.påbegyndt` og før 3 måneder efter denne dato.
        Redundant, når `oprettet` haves?
    """
    stillet =DateField(
        help_text='Dato, hvor opgaven blev stillet til elev (eller hold)'
    ) 
    """Afleveringsfrist Valideres til at ligge efter `stillet` og højst 3 måneder efter denne dato."""
    frist = DateTimeField(help_text='Dato og tid for seneste aftalte aflevering')
    """
        Gerne oprettelses-tidsstempel fra video-netside
        Valideres til at ligge efter `frist` og højst 3 måneder efter `frist`.
    """
    indleveret = DateField(help_text='Dato og tid for faktisk aflevering') 
    opgave = CharField(max_length=100, help_text='Opgavetekst for SOLO aktivitet')
    #"""
    #    Knytter eventuelt opgaven, og dermed præsentationen,
    #    til en HookED On Thinking aktivitet. 
    #    I bekræftende fald giver relationen et paradigmatisk - ikke opgave-konkret - 
    #    SOLO-retteark til SOLO-niveau.
    #"""
    # solo_aktivitet ManyToManyField
    url = URLField(help_text='Videoens placering (fx skjult på YouTube)')
    egen_solo  = CharField(
        max_length=3,
        choices=[
            ('pre', 'Præstrukturelt niveau'), 
            ('uni', 'Unistrukturelt niveau'), 
            ('mul', 'Multistrukturelt niveau'), 
            ('rel', 'Relationelt niveau'), 
            ('udv', 'Udvidet-abstrakt niveau')
        ], 
        null=True,
        verbose_name="Elevens egen bedømmelse efter SOLO"
    )
    """Hvis feltet udfyldes, sker det EFTER elevens egen SOLO bedømmelse."""
    lærer_solo = CharField(
        max_length=3,
        choices=[
            ('pre', 'Præstrukturelt niveau'), 
            ('uni', 'Unistrukturelt niveau'), 
            ('mul', 'Multistrukturelt niveau'), 
            ('rel', 'Relationelt niveau'), 
            ('udv', 'Udvidet-abstrakt niveau')
        ], 
        null=True
    )
    """ i stedet for (eller som supplement til) SOLO-bedømmelse """
    egen_bedømmelse  = CharField(
        max_length=100, null=True,
        verbose_name="Elevens egen bedømmelse i fri tekst"
    )
    """
        I stedet for (eller som supplement til) SOLO-bedømmelse. 
        Hvis feltet udfyldes, sker det efter elevens egen bedømmelse.
    """
    lærer_bedømmelse = CharField(
        max_length=100, null=True
    )
    
    class Meta:
        ordering = ['forløb', 'frist', 'elev']

    def __str__(self):
        return self.__class__.__name__ + f" fra {self.elev} indleveret d. {self.indleveret}."

    def get_absolute_url(self):
        """Returnerer URL, der tilgår en bestemt Video."""
        return reverse('videopraesentation-detalje-visning', args=[str(self.id)])
