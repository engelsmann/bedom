from django.db               import models
from django.urls             import reverse
from django.core.validators  import MaxValueValidator, MinValueValidator
from django.db.models.fields import AutoField


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
    elev_fg_runde_id = AutoField(verbose_name='Fokusgruppens Elev-løbenummer')
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


