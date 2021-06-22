OS2bos og rammearkitekturen
===========================

Målgruppe
---------
Denne tekst indeholder en kort analyse af forholdet mellem systemet
OS2bos og den fælleskommunale rammearkitektur. Den er skrevet i oktober
2020 på baggrund af OS2bos version 3.2.1.

Det forudsættes, at læseren kender OS2bos-systemet og i det mindste har
et vist overblik over dets
`datamodel <https://raw.githubusercontent.com/OS2bos/os2bos/master/backend/docs/graphics/OS2BOS_datamodel.png>`_; 
endvidere forudsættes et (ikke nødvendigvis dybtgående) kendskab til den
fælleskommunale rammearkitektur.

Anbefalingerne herunder skal ikke forstås som en facitliste, ligesom
gennemgangen ikke er udtømmende - læseren er velkommen til at drage sine
egne konklusioner og komme med supplerende forslag til, hvad der kan
ændres.


Konklusion og anbefalinger
--------------------------

Der er i store træk sammenfald mellem datamodellen i OS2bos og den
fælleskommunale rammearkitekturs "treenighed" Ydelse, Bevilling og
Effektuering. I det omfang, der ikke er, vil det for det meste ikke
være vanskeligt at konvertere mellem de to repræsentationer.

Den største afvigelse fra dette mønster er begrebet "hovedydelse" i
OS2bos, som ikke eksisterer i rammearkitekturens byggeblokke. Hvis man
skulle importere data til OS2bos via et format baseret på disse, ville
man være nødt til på anden vis at regne ud, hvilken ydelse var
hovedydelse for hver bevilling; den anden vej ville der ikke være noget
problem.

Bortset fra denne modelleringsmæssige inkompatibilitet ville følgende
tiltag bringe OS2bos tættere på rammearkitekturens begreber og modeller:

* Klassen ``Activity`` kan omdøbes til ``GrantedService`` for at svare
  til rammearkitekturens BevilgetYdelse.
* Klassen ``ActivityDetails`` kan omdøbes til ``Service`` for at svare
  til rammearkitekturens Ydelse.
* Reglerne for kontering parametriseres, sådan at de kan afhænge af Ydelse
  eller måske organisationsenhed e.l., og håndteres f.eks. ved hjælp af
  Python-idiomet for et Strategi-pattern.
* Det overvejes, om noget lignende er nødvendigt mht. reglerne for for 
  beregning og bevilling.
* Det overvejes, om den nuværende implementation af beregningsreglen
  er bitemporal nok i forhold til rammearkitekturens intentioner.

Man kunne også overveje at ændre navnene på klasserne
``PaymentSchedule`` og ``Payment``, så de bedre svarer til noget fra
byggeblokken Effektuering, men OS2bos er så fokuseret på økonomi, at
de nuværende navne umiddelbart giver bedre mening.

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
+++

En `Sag
<https://rammearkitektur.kl.dk/indhold-i-rammearkitekturen/optaget-i-rammearkitekturen/optagede-byggeblokke/sag/>`_
i rammearkitekturen - hvilket svarer til et objekt af klassen ``Case``
OS2bos - repræsenterer en sag i et eksternt journaliseringssystem, i
Ballerups tilfælde SBSYS.

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
+++++++++

Byggeblokken `Bevilling
<https://rammearkitektur.kl.dk/indhold-i-rammearkitekturen/optaget-i-rammearkitekturen/optagede-byggeblokke/bevilling/>`_
består af to klasser ved navn Bevilling og BevilgetYdelse, der svarer til
klasserne ``Appropriation`` og ``Activity`` i OS2bos.

De forskellige klasser i byggeblokken Bevilling ses herunder:

.. image:: https://rammearkitektur.kl.dk/media/22889/bevilling-informationsmodel.png?width=700

Ved sammenligning af byggeblokkens Bevilling med klassen
``Appropriation`` i OS2bos findes, at

* der ikke er nogen eksplicit *Bevillingsmodtager* på ``Appropriation``.
  Implicit er det altid sagsparten, som ydelsen "kommer til gode", så
  denne værdi er indirekte fastlagt gennem ``Case``-objektet.
* *Bevillingsgiver* er implicit altid den relevante afdeling i CBUR, men
  det fremgår også, hvem der har godkendt ydelser på en sag og hvornår.
* I rammearkitekturen er en bevilling ikke forbundet med en paragraf i
  serviceloven, som tilfældet er i OS2bos. I rammearkitekturen ligger
  dette på sagsniveau i form af *Sagshjemmel*, som nævnt under
  gennemgangen af Sag. I OS2bos svarer lovparagraffen
  netop også til en oplysning ikke på hovedsagen, men på
  foranstaltningssagen i SBSYS.
* I modsætning til i rammearkitekturen har en bevilling i CBUR ikke
  nogen eksplicit start- og slutdato. Dette fastlægges i stedet gennem
  hovedydelsens start- og slutdato.

Ideen om en *hovedydelse* er en klar forskel mellem datamodellen i
OS2bos og rammearkitekturens byggeblok. For så vidt som hovedydelsen kan
pålægge begrænsninger, der gælder for samtlige ydelser i en bevilling,
kunne disse begerænsninger egentlig også have været udtrykt som en
egenskab ved bevillingen - for eksempel start- og slutdato, som vi lige
har set.

Ved sammenligning af byggeblokkens BevilgetYdelse med klassen
``Activity`` i OS2bos findes, at 

* rammearkitekturen ikke fastlægger, om selve godkendelsen af en
  bevilling skal ske på bevillings- eller ydelsesniveau - i OS2bos
  foregår det på ydelsesniveau, således at hver ydelse i en bevilling
  har tilknyttet en godkendende bruger (en Aktør i rammearkitekturens
  sprog). 
* Derudover indeholder hver ``Activity`` eksplicit en reference til en
  konkret leverandør, hvilket ikke er modelleret i rammearkitekturen.
* OS2bos giver heller ikke mulighed for at specificere, at en ydelse er
  tilbagebetalingspligtig - enten er det ikke relevant for nogen af
  vores use cases, eller også håndteres det andetsteds.

Modelleringen i OS2bos adskiller sig lidt fra rammearkitekturen ved at
lægge "snittet" mellem bevilling- og ydelses-området mellem
``Appropriation`` og ``Activity``, hvorimod rammearkitekturen lægger det
mellem BevilgetYdelse og Ydelse.


Ydelse
++++++

Byggeblokken `Ydelse <https://rammearkitektur.kl.dk/indhold-i-rammearkitekturen/optaget-i-rammearkitekturen/optagede-byggeblokke/ydelse/>`_
svarer til klassen (klassifikationen) ``ActivityDetails`` i OS2bos.

Sidstnævnte indeholder alle oplysninger, som er nødvendige for at kunne
registrere, prisberegne og kontere (fakturere) en ydelse.

De forskellige klasser i byggeblokken Ydelse ses herunder:

.. image:: https://rammearkitektur.kl.dk/media/23357/informationsmodel-ydelse.png?width=700

Det skal bemærkes, at eftersom OS2bos er et *økonomi*-styringssystem,
behandles alle ydelser reelt som økonomiske ydelser - mange af dem kunne
måske bedst beskrives som fysiske ydelser eller ressourceydelser, men i
OS2bos interesserer vi os kun for det økonomiske aspekt, og alle ydelser
behandles på samme måde.

Derudover adskiller modellen i OS2bos sig fra rammearkitekturen på
følgende punkter:

* *Bevillingsregel* er ikke modelleret som et objekt, men fremgår i stedet af
  relationen ``SectionInfo`` mellem ``ActivityDetails`` og
  klassifikationen ``Section``, der indeholder servicelovens
  paragraffer - hver ydelse er knyttet til 0 eller flere paragraffer,
  efter hvilke den kan være hoved- eller følgeydelse.
* *Konteringsregel* er heller ikke modelleret som et objekt, men fremgår
  (med den nye metode) af relationen ``AccountAliasMapping`` mellem
  ``ActivityDetails`` og ``SectionInfo``.
* *Beregningsregel* er heller ikke modelleret som et objekt, men er
  implementeret i form af prisoplysningerne på ``PaymentSchedule``, der
  ca. svarer til rammearkitekturens EffektueringsPlan.
* Det anbefales, at oplysningerne, der anvendes af Beregningsreglen er
  bitemporale, så de altid kan genberegnes. Det er de i dag, for så vidt
  som de er Takster og Priser, dvs. hvis en pris er beregnet pr. enhed.
* I OS2bos hænger relationen mellem Lovgrundlag og klassificering
  sammen, idet KLE-numre er knyttet til relationen mellem Lovgrundlaget
  og Ydelsen (``Section`` og ``ActivityDetails``).
* Da OS2bos ikke primært beskæftiger sig med ydelser, der udbetales til
  ydelsesmodtageren (sagsparten) i form af penge, er mange af
  rammearkitekturens felter vedrørende Økonomisk Ydelse ikke relevante -
  og dem, der *er* relevante, gemmes på betalingsplanen.

En mulig observation er her, at hvis OS2bos fremadrettet skal håndtere
bevillinger på andre områder end det sociale og af andre typer ydelser,
ville det ganske givet være en god idé at have en parametrisering af
reglerne for kontering, bevilling og beregning og knytte dem enten til
den enkelte Ydelse eller måske til en mere overordnet (og fremtidig)
opdeling i systemet - svarende til det klassiske design pattern
Strategi.


Effektuering
++++++++++++

Byggeblokken `Effektuering
<https://rammearkitektur.kl.dk/indhold-i-rammearkitekturen/optaget-i-rammearkitekturen/optagede-byggeblokke/effektuering/>`_
repræsenteres af klasserne ``PaymentSchedule`` og ``Payment`` i
OS2bos.

De forskellige klasser i byggeblokken Effektueringsplan ses herunder:

.. image:: https://rammearkitektur.kl.dk/media/22893/effektuering-informationsmodel.png?width=626.944971537002&height=700

En ikke uvæsentlig detalje er her, at en effektuering af en af de
ydelser, som behandles i OS2bos, kan være noget mere omstændeligt, end
hvad systemet behøver at forholde sig til. Hvis et ungt menneske for
eksempel får bevilget en kontaktperson, består effektueringen i at finde
en kontaktperson, i at få arrangeret, at denne kontakter familien, i
kontaktpersonens fysiske møder med den unge ... og selvfølgelig også i
betalingen for denne ydelse. For OS2bos består effektueringen kun i
beregningen af, hvad der skal betales hvornår.

Klasserne ``PaymentSchedule`` og ``Payment`` svarer dermed bedst til
klasserne Økonomisk Effektueringsplan og Økonomisk Ydelseseffektuering i
rammearkitekturen.

"Samleklassen" Økonomisk Effektuering, der indeholder effektueringen af
de enkelte ydelser, repræsenterer den faktiske udbetaling af de
forfaldne betalinger og håndteres ikke i OS2bos. Dog kan eksporten af
betalinger til PRISME siges at udgøre den Økonomiske Effektuering af
disse betalinger, men den er ikke medtaget i OS2bos' datamodel som
selvstændigt objekt.

Den primære forskel imellem disse er, at klassen ``Payment`` i OS2bos
ikke har en periode, kun en udbetalingsdato, der kan siges at svare til
dispositionsdato i diagrammet herover. Herudover svarer
OS2bos' ``PaymentSchedule``-klasse nøje til, hvad der er beskrevet i
rammearkitekturen, hvor vi læser:

    Ofte er økonomiske ydelser kendetegnet ved gentagen udbetaling af et
    beløb - eksempelvis en gang månedligt, startende på en bestemt dag.

    Effektueringsplanen (for økonomisk ydelse) indeholder således informationer som:

    - startdato
    - frekvens (måned, uge etc.)
    - udbetalingsdag ("sidste bankdag", "sidste torsdag i måneden" etc)
    - beløb (et "alt andet lige"-beløb, som ændres, hvis forholdene ændres)



