<template>

    <div class="payment-plan">
        <h2>Betalingsplan</h2>
        <template v-if="type === 'ONE-TIME-PAYMENT'">
            Der betales {{ amount }} kr én gang
        </template>

        <template v-if="type === 'RUNNING-PAYMENT'">
            Der betales {{ amount }} kr hver {{ freq_name }}
        </template>

        <template v-if="type === 'PER-HOUR-PAYMENT' || type === 'PER-DAY-PAYMENT' || type === 'PER-KM-PAYMENT'">
            Der betales {{ amount }} kr pr 
        </template>
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
                        str += `${ this.amount } kr pr time`
                        break
                    case 'PER-DAY-PAYMENT':
                        str += `${ this.amount } kr pr døgn`
                        break
                    case 'PER-KM-PAYMENT':
                        str += `${ this.amount } kr pr kilometer`
                        break
                    default:
                        str += 'intet'
                }

                return str
            },
            freq_name: function() {
                switch(this.frequency) {
                    case 'PAY-EVERY-MONTH':
                        return 'måned'
                        break
                    case 'PAY-EVERY-WEEK':
                        return 'uge'
                        break
                    case 'PAY-EVERY-DAY':
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