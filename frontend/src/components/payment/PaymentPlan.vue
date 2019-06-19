<template>

    <div class="payment-plan">
        <h2>Betalingsplan</h2>
        {{ abstract }}

        <table>
            <tbody>
                <tr>
                    <td>
                        I alt pr år
                    </td>
                    <td style="text-align: right;">
                        <strong>{{ yearly_cost }} kr</strong>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

</template>

<script>

    export default {

        props: [
            'amount',
            'units',
            'type',
            'frequency'
        ],
        data: function() {
            return {
                freq_factor: 0,
                month_factor: 0,
                months: [
                    'januar',
                    'februar',
                    'marts',
                    'april',
                    'maj',
                    'juni',
                    'juli',
                    'august',
                    'september',
                    'oktober',
                    'november',
                    'december'
                ]
            }
        },
        computed: {
            abstract: function() {
                let str = 'Der betales '

                switch(this.type) {
                    case 'ONE-TIME-PAYMENT':
                        str += `${ this.amount } kr én gang`
                        break
                    case 'RUNNING-PAYMENT':
                        str += `${ this.amount } kr pr ${ this.freq_name }`
                        break
                    case 'PER-HOUR-PAYMENT':
                        str += `${ this.amount } kr pr time - ${ this.units } timer pr ${ this.freq_name }`
                        break
                    case 'PER-DAY-PAYMENT':
                        str += `${ this.amount } kr pr døgn - ${ this.units } døgn pr ${ this.freq_name }`
                        break
                    case 'PER-KM-PAYMENT':
                        str += `${ this.amount } kr pr kilometer - ${ this.units } kilometer pr ${ this.freq_name }`
                        break
                    default:
                        str += 'intet'
                }

                return str
            },
            yearly_cost: function() {
                let num = 0
                switch(this.type) {
                    case 'ONE-TIME-PAYMENT':
                        num = this.amount
                        break
                    case 'RUNNING-PAYMENT':
                        num = this.amount * this.freq_factor
                        break
                    default:
                        num = this.amount * this.freq_factor * this.units
                }
                return num
            },
            freq_name: function() {
                switch(this.frequency) {
                    case 'PAY-EVERY-MONTH':
                        this.freq_factor = 12
                        this.month_factor = 1
                        return 'måned'
                        break
                    case 'PAY-EVERY-WEEK':
                        this.freq_factor = 52
                        this.month_factor = 4
                        return 'uge'
                        break
                    case 'PAY-EVERY-DAY':
                        this.freq_factor = 365
                        this.month_factor = 31
                        return 'dag'
                        break
                    default:
                        return 'ukendt'
                }
            }
        },
        methods: {

            
        }

    }
    
</script>