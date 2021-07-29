from django.db               import models
from django.db.models.fields.related import ForeignKey
from django.urls             import reverse
from django.core.validators  import MaxValueValidator, MinLengthValidator, MinValueValidator
from django.db.models.fields import AutoField, BooleanField, CharField, DateField, IntegerField, TextField


# Create your models here.

class Skole(models.Model):
    """Samle-struktur (klasse) for klasser. En lærer vil være tilknyttet (mindst 1) skole."""

    # Fields
    navn = models.CharField(max_length=100, help_text='Skolens officielle navn')
    kortnavn = models.CharField(max_length=20, help_text='Skolens korte navn')

    # Metadata
    class Meta:
        ordering = ['navn']

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
    skole = models.ForeignKey('Skole', on_delete=models.RESTRICT, null=True)
    startår = models.IntegerField(validators=[ MinValueValidator(1950), MaxValueValidator(2050)], help_text='Firecifret årstal for holdstart')
    """Fortløbende nummerering af den runde/omgang af samplinger, https://trello.com/c/mDSvj2t2 , klassens elever sættes sammen i, i fokusgrupper """
    fokus_runde = models.IntegerField(validators=[ MinValueValidator(0), MaxValueValidator(999)], help_text='(automatisk) løbenummer for samplingsrunde til fokusgruppe')
    """Antal medlemmer i fokusgruppe"""
    fokus_antal = models.IntegerField(validators=[ MinValueValidator(0), MaxValueValidator(35)], help_text='Standardstørrelse af klassens fokusgruppe')
    note = models.TextField(max_length=200, help_text='Lærerens generelle noter om holdet, dets lokale eller historik')

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
    id = models.UUIDField(primary_key=True)
    fornavn = models.CharField(max_length=50, help_text='Personens officielle fornavn(e) som i protokol')
    efternavn = models.CharField(max_length=50, help_text='Personens officielle efternavn(e) som i protokol')
    kaldenavn = models.CharField(max_length=15, help_text='Det navn, personen ønsker brugt i daglig tiltale')
    klasse = models.ForeignKey('Klasse', on_delete=models.RESTRICT, null=True)
    unilogin = models.CharField(min_length=8, max_length=8, help_text='Personens officielle fornavn(e) som i protokol')
    mail = models.EmailField(help_text='Mail, læreren kan bruge til kommunikation med eleven')
    # https://stackoverflow.com/q/19130942/888033
    mobil = models.CharField(min_length=8, max_length=15, help_text='Mobiltelefonnummer, system og lærer kan bruge til kommunikation med eleven')
    note = models.TextField(max_length=200, help_text='Lærerens noter om eleven, elevens lokale eller historik. OBS der er mulighed andetsteds for løbende observationsnoter.')

    class Meta:
        ordering = ['klasse', 'fornavn', 'efternavn']
        verbose_name = 'elev'
        verbose_name_plural = 'elever'

    # Methods
    def get_absolute_url(self):
        """Returnerer URL, der tilgår en bestemt instantiering af klassen Klasse (et bestemt hold)."""
        return reverse('elev-detalje-visning', args=[str(self.id)])

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
    """

    # Fields
    elev_fg_runde_id = AutoField(primary_key=True, verbose_name='Fokusgruppens Elev-løbenummer')
    """Klasse (og dermed `Elev.Klasse.fokus_runde`), samt Elev gives af denne relation."""
    elev = models.ForeignKey('Elev', on_delete=models.RESTRICT, null=True)
    """
        Modul udfyldes ikke ved generering af del-liste, 
        først når læreren udvælger hvor mange, der skal observeres i det pågældende Modul.
        Dato (og tid) gives af denne relation.
    """
    modul = models.ManyToManyField('Modul', on_delete=models.RESTRICT, null=True)
    """
        Eleven i en instantiering (række) præsenteres i liste over Fokusgruppe-kandidater,
        hvis bedømt=False eller =Null. Sættes til =True, når observation registreres.
    """
    bedømt = models.BooleanField(null=True)
    """Runde af observation, fra Elev.Klasse.fokus_runde (redundant)."""
    runde = models.ForeignKey('Elev.Klasse.fokus_runde', on_delete=models.RESTRICT, null=True)
    """
        Tilfældig værdi mellem 0 og 1, der tildeles ved oprettelse.
        Sorteringsværdi (indenfor Elev.Klasse.fokus_runde). 
    """
    rand_rank = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])

    class Meta:
        ordering = ['elev_fg_runde_id', 'elev.id']
        verbose_name = 'fokusgruppe til adfærdsobservation'
        verbose_name_plural = 'fokusgrupper til adfærdsobservation'

    # Methods
    """Giver 'baglæns' URL-kodning mening for denne Model?"""
    def get_absolute_url(self):
        """Returnerer URL, der tilgår en bestemt instantiering af klassen Klasse (et bestemt hold)."""
        return reverse('fokusgruppe-detalje-visning', args=[str(self.id)])

    def __str__(self):
        """Streng, som repræsenterer Elev (på Admin siden etc.)."""
        return f"{self.elev.fornavn} {self.elev.efternavn} ({self.klasse.fokus_runde}, {self.klasse.kortnavn})"

class Emne(models.Model):
    """Faglige emner, som danner rammen om forløb for de enkelte klasser"""
    id = AutoField(primary_key=True, verbose_name='Emne-løbenummer (automatisk)')
    titel = CharField(max_length=20, help_text='Betegnelse for emnet')
    fag = CharField(choices=['Matematik', 'Informationsteknologi'], default='Matematik')
    studieretning = CharField(choices=['stx','hf','htx','hhx','eux','eud','andet'], default='stx', help_text='Klassens studieretning')
    faglige_mål = TextField(max_length=1000, help_text='Bekendtgørelsens og skolens faggruppes krav til emnet')
    note = TextField(max_length=1000, help_text='Lærerens krav til og ambitioner for emnet')
    klassetrin = IntegerField(min_value=1, max_value=4, help_text='Årgang, emnet undervises på (siden holdets startår)')
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
    titel = CharField(max_length=20, help_text='Overskrift for forløbet')
    påbegyndt = DateField(help_text='Dato for planlagt start af forløbet')
    varighed = IntegerField(help_text='Forventet antal lektioner/moduler')
    kommentar = TextField(max_length=500,help_text='Præsentation til holdets elever af det konkrete forløb i klassen')
    class Meta:
        ordering = ['klasse', 'emne']
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
    afholdt = DateField(help_text='Dato for planlagt start af forløbet')
    class Meta:
        ordering = ['afholdt', 'id']
        verbose_name_plural='moduler'
    def __str__(self):
        return f"Modul {self.id} '{self.forløb.titel}', {self.afholdt} ({self.forløb.klasse})."
    def get_absolute_url(self):
        """Returnerer URL, der tilgår et bestemt Modul."""
        return reverse('modul-detalje-visning', args=[str(self.id)])

class Adfærd(models.Model):
    """
    De to sociale performance indicators er intenderet til at stimulere/måle elevernes 'Decency Quotient'. 
    Den faglige er til at stimulere/måle 'Intelligenskvitient'.
    Scores kan alene registreres (not Null), hvis `tilstede`=True (observation ikke mulig af fraværende elever).
    """
    id = AutoField(primary_key=True,verbose_name='Løbenummer (automatisk) for adfærdsobservation')
    modul        = ForeignKey('Modul',       on_delete=models.RESTRICT, null=True)
    fokusgruppe  = ForeignKey('FokusGruppe', on_delete=models.RESTRICT, null=True)
    tilstede = BooleanField(default=True)
    spørg  = IntegerField(validators=[MinValueValidator(1),MaxValueValidator(4)], null=True, help_text='Score for elevens evne til at søge hjælp på fagligt spørgsmål')
    hjælp  = IntegerField(validators=[MinValueValidator(1),MaxValueValidator(4)], null=True, help_text='Score for elevens evne til at yde hjælp til faglig problemløsning')
    faglig = IntegerField(validators=[MinValueValidator(1),MaxValueValidator(4)], null=True, help_text='Score for elevens evne til at bidrage til en faglig samtale')
    stikord  = CharField(max_length=30, help_text='Lærerens observationer i ord')
    reaktion = CharField(max_length=30, help_text='Elevens bemærkning')

    class Meta:
        ordering = ['']
        verbose_name='adfærdsobservation'
        verbose_name_plural='adfærdsobservationer'

    def __str__(self):
        return f"Adfærd #{self.id} af {self.fokusgruppe.elev} observeret d. {self.modul.afholdt}:\n{self.spørg}/{self.hjælp}/{self.faglig}"
    def get_absolute_url(self):
        """Returnerer URL, der tilgår observationer af en bestemt Elev i et bestemt Modul."""
        return reverse('adfaerd-detalje-visning', args=[str(self.id)])
