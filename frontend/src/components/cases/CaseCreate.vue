<template>
    <section class="case-form">
        <h1>Opret sag</h1>
        <form>
            <fieldset>
                <label for="inputSearch">SBSYS Hovedsag:</label>
                <input id="inputSearch" type="search">
                <button class="case-button">Hent</button>
            </fieldset>

            <fieldset>
                <label>Sagspart:</label>
                <dl>
                    <dt>CPR-nr:</dt>
                    <dd>211212-1111</dd>
                    <dt>Navn:</dt>
                    <dd>Ole Henriksen</dd>
                </dl>
            </fieldset>

            <label>Familie og relationer:</label>
            <fieldset>
                <label>Forældre:</label>
                <dl>
                    <dt>Mor:</dt>
                    <dd>Ole Henriksen</dd>
                    <dt>Far:</dt>
                    <dd>Ole Henriksen</dd>
                    <dt>Andre:</dt>
                    <dd>Ole Henriksen</dd>
                </dl>
            </fieldset>

            <label>Kommune:</label>
            <fieldset>
                <label for="selectField1">Betalingskommune:</label>
                <select id="selectField1">
                    <option>Ballerup Kommune</option>
                    <option>Herlev Kommune</option>
                    <option>Solrød Kommune</option>
                </select>
            </fieldset>
            <fieldset>
                <label for="selectField2">Handlekommune:</label>
                <select id="selectField2">
                    <option>Ballerup Kommune</option>
                    <option>Herlev Kommune</option>
                    <option>Solrød Kommune</option>
                </select>
            </fieldset>
            <fieldset>
                <label for="selectField3">Bopælsskommune:</label>
                <select id="selectField3">
                    <option>Ballerup Kommune</option>
                    <option>Herlev Kommune</option>
                    <option>Solrød Kommune</option>
                </select>
            </fieldset>

            <fieldset>
                <label>Målgruppe:</label>
                <input id="inputRadio1" type="radio" name="radioButtonSet">
                <label for="inputRadio1">Familieafdelingen</label>
                <input id="inputRadio2" type="radio" name="radioButtonSet">
                <label for="inputRadio2">Handicapafdelingen</label>
            </fieldset>

            <label>Andet:</label>
            <fieldset>
                <input id="inputCheckbox1" type="checkbox" name="radioButtonSet">
                <label for="inputCheckbox1">Integrationsindsatsen</label>
                <input id="inputCheckbox2" type="checkbox" name="radioButtonSet">
                <label for="inputCheckbox2">Tværgående ungeindsats</label>
            </fieldset>
            <fieldset>
                <label for="selectField">Oprindeligt distrikt:</label>
                <select id="selectField">
                    <option>Skovvejen</option>
                    <option>Ballerupvej</option>
                    <option>Hestevejen</option>
                </select>
            </fieldset>
            <fieldset>
                <dt>Indsatstrappen:</dt>
                <dd>4</dd>
                <dt>Skaleringstrappe:</dt>
                <dd>5</dd>
                <button>Vurdering</button>
            </fieldset>

            <label>Sagsbehandling:</label>
            <fieldset>
                <dt>Sagsbehander:</dt>
                <dd>Leif Lyngby Lodahl (leil)</dd>
                <dt>Team:</dt>
                <dd>Familieteamet</dd>
                <label for="selectField">Distrikt:</label>
                <select id="selectField">
                    <option>Skovvejen</option>
                    <option>Ballerupvej</option>
                    <option>Hestevejen</option>
                </select>
                <fieldset>
                    <dt>Leder:</dt>
                    <dd>Jens Kjellerup Hansen</dd>
                </fieldset>
            </fieldset>
            <fieldset>
                <button>Gem</button>
            </fieldset>
        </form>
    </section>

</template>

<script>

</script>

<style>

    .case-form {
        margin: 1rem;
    }
    .case-button {
        margin-left: 1rem;
    }

</style>