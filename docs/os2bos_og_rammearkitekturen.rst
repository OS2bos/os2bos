OS2bos og rammearkitekturen
===========================

Indledning
----------

Der findes to sæt af Rammearkitektur-byggeblokke, som kan bruges til at
beskrive indsatser og bevillinger på det sociale område, nemlig
Tilstand, Indsats og Aktivitet samt Ydelse, Bevilling og Effektuering.

Ydelse, Bevilling og Effektuering blev først godkendt som byggeblokke
den 16. december 2019, hvilket betyder, at vi ikke var opmærksomme på
dem ved det initielle design af OS2bos i foråret 2019.

I det første udkast til byggeblokkene Tilstand, Indsats og Aktivitet
havde disse et betydeligt overlap med de oplysninger, vi behandler i
OS2bos, idet Indsats og Aktivitet kunne indeholde oplysninger om pris,
bevilgende myndighed, og så videre. Disse elementer er imidlertid
mindre fremtrædende i den nugældende udgave af Tilstand, Indsats og
Aktivitet, der blev godkendt og officielt optaget i Rammearkitekturen i
juli 2018, formentlig fordi arbejdet med Ydelse, og Bevilling og
Effektuering allerede var påbegyndt på det tidspunkt.

Det er imidlertid klart, at begge sæt af byggeblokke kan anvendes til at
beskrive forskellige aspekter af indsatser på det sociale område.

En person med behov for hjælp fra en offentlig myndighed (i dette
tilfælde et udsat barn eller en borger med handicap) vil således have
brug for en Indsats, der kan afhjælpe dette behov, og i praksis vil
denne Indsats bestå af en række Aktiviteter, og denne indsats vil have
et mål - hvilket også kan beskrives som en ændring i modtagerens
Tilstand (f.eks. forbedret trivsel hos et barn, der har fået en
kontaktperson).

En bevilling i OS2bos kan således opfattes som noget, der repræsenterer
en Indsats, og de tilhørende enkeltydelser kan ses som Aktiviteter -
mens oplysningerne om modtagerens nuværende status, som i OS2bos er
indkodet i Indsatstrappen og Skaleringstrappen, kan siges at
repræsentere en nuværende Tilstand. 

Tilstand, Indsats og Aktivitet har imidlertid fokus på at beskrive de
*kvalitative* aspekter af de forskellige indsatser: Er der tale om en
pædagogisk eller psykologisk indsats, hvor foregår den, hvilke
hjælpemidler anvendes, osv. Byggeblokken Indsats lægger også op til at
modellere Aktiviteter vedrørende indstilling og beslutning, altså
aktiviteter, der er en del af kommunens sagsbehandling og ikke modelleres
som udgifter i BOS.

Tilstand, Indsats og Aktivitet ville derfor være naturlige at bruge i et
egentligt sagsbehandlingssystem, hvor oplysningerne om de enkelte
ydelsers (eller aktiviteters) kvalitative indhold er vigtig, og hvor
kommunens egne beslutningsprocesser i form af indstillingsmøder,
beslutningsmøder, evalueringsmøder osv. også indgår i processen.

OS2bos er derimod karakteriseret ved at være et
*økonomi*-styringssystem: Ydelserne er defineret ved de regler og
paragraffer, de kan bevilges efter, og derudover er det de økonomiske
aspekter af dem, der er interessante: Hvad koster de, hvordan afregnes
de, hvordan og hvor ofte skal der betales for dem. Og det er netop det,
som byggeblokkene Ydelse, Bevilling og Effektuering bedst kan beskrive.

Man kunne imidlertid godt fra BOS udtrække oplysninger, der var
relevante for en "Tilstand, Indsats, Aktivitet"-beskrivelse: Hvilke
indsatser sættes ind ved hvilke tilstande, hvad koster de, hvor lang tid
tager de, og hvilke af dem fører ifølge data erfaringsmæssigt til en
forbedring af modtagerens velbefindende. Denne kobling virker oplagt nok
til, at det kan undre, at der i den nuværende rammearkitektur slet ikke
er beskrevet nogen kobling mellem Indsats og Bevilling.

Dette fører umiddelbart til denne konklusion for OS2bos' position i
forhold til rammearkitekturen:

* Systemets design bør ligge tæt op af byggeklodserne Ydelse, Bevilling og
  Effektuering og ikke mindst indeholde de samme oplysninger som disse
  byggeklodser, ikke nødvendigvis i helt samme format; og
* Systemet kan med fordel være leverandør af data til analyser baseret
  på Tilstand, Indsats og Aktivitet, ikke mindst med henblik på en
  empirisk observation af, hvilke indsatser (herunder, hvilke
  leverandører af hvilke ydelser) der lader til at virke bedst.
* Ud over de helt centrale byggeblokke Ydelse, Bevilling og Effektuering
  arbejde OS2bos med begreber fra andre dele af rammearkitekturen -
  ikke mindst byggeblokkene Sag og Klassifikation. Disse vil blive
  behandlet i den følgende gennemgang af systemets enkelte klasser og
  deres relationer til byggeblokkene.

Det skal også bemærkes at OS2bos kan indeholde udvidelser i forhold til
rammearkitekturen, hvormed menes oplysninger, som der ikke er lagt op
til i byggeblokkene, men som hører hjemme i det sociale område, som
OS2bos er udviklet til.

OS2bos: Klasser og byggeblokke
------------------------------


Sag
---

En `Sag <https://rammearkitektur.kl.dk/media/23306/sag-informationsmodel.png?width=700&height=453.0674846625767>`_
i OS2bos - et objekt af klassen ``Case`` - repræsenterer en sag i
et eksternt journaliseringssystem, i Ballerups tilfælde SBSYS.

Byggeblokkens klassestruktur ses her:

.. image:: https://rammearkitektur.kl.dk/media/23305/sag-objektmodel.png?width=700

Sammenligner vi dette diagram med OS2bos' objektmodel har vi, at

* *Sagspart* er repræsenteret af modtagerens navn og CPR-nummer.
* *Sekundærparter* er repræsenteret af klassen "relaterede personer" ved
  klassen ``RelatedPerson``, der indeholder navn, CPR-nummer samt
  relationstype for f.eks. sagspartens familiemedlemmer.
* *Sagshjemmel* er implicit gennem relationen til SBSYS, fordi SBSYS-ID
  henviser til en paragraf i Service-loven.
* *Emneklasse* mv. er ikke direkte repræsenteret, men hører i høj grad
  også til i journaliseringssystemet snarere end i OS2bos. Oplysninger, der
  vedrører kontering, ligger i OS2bos ikke på sags- men på ydelses- og
  paragraf-niveau.
* Relationerne til *Sagsaktør* repræsenteres i OS2bos af sagens team og
  sagsbehandlere samt handle- og betalingskommune. Alle sager i OS2bos
  tilhører implicit CBUR i Ballerup Kommune.
* Sagen har ikke direkte noget tilknyttet *Dokument*, men
  bevillingsskrivelser journaliseres via de bevillinger
  (foranstaltningssager i SBSYS), sagen "ejer".
* *Journalnotat* er ikke repræsenteret i OS2bos og antages at høre hjemme
  i journaliseringssystemet.

Herudover indeholder en sag i OS2bos oplysninger, som CBUR har brug for
i sit arbejde med sagen - skoledistrikt, oplysning om indplacering på
skalerings- og indsatstrappe, samt om Andre Indsatser.

Desuden kan en sag indeholde et vilkårligt antal bevillinger, som
behandles i næste afsnit·

Bevilling
---------

Byggeblokken `Bevilling
<https://rammearkitektur.kl.dk/indhold-i-rammearkitekturen/optaget-i-rammearkitekturen/optagede-byggeblokke/bevilling/>`_
svarer til klassen ``Appropriation`` i OS2bos.

De forskellige klasser i byggeblokken Bevilling ses herunder:

.. image:: https://rammearkitektur.kl.dk/media/22889/bevilling-informationsmodel.png?width=700

Ved sammenligning med klassen ``Appropriation`` i OS2bos findes, at

* der ikke er nogen eksplicit *Bevillingsmodtager* på ``Appropriation``.
  Implicit er det altid sagsparten, som ydelsen "kommer til gode", så
  denne værdi er indirekte fastlagt gennem ``Case``-objektet.
* *Bevillingsgiver* er implicit altid den relevante afdeling i CBUR, men
  det fremgår også, hvem der har godkendt ydelser på en sag og hvornår.
* I modsætning til i rammearkitekturen har en bevilling i CBUR ikke
  nogen eksplicit start- og slutdato. Dette fastlægges i stedet gennem
  hovedydelsens start- og slutdato.
