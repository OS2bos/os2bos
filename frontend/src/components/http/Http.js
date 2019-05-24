import axios from 'axios'
import spinner from '../spinner/Spinner.js'

const ax = axios.create({
    baseURL: '/api'
})

ax.interceptors.request.use(
    function (config) {
        spinner.spinOn()
        return config
    },
    function (err) {
        return Promise.reject(err)
    }
)

ax.interceptors.response.use(
    function (res) {
        spinner.spinOff()
        return res
    },
    function (err) {
        spinner.spinOff()
        return Promise.reject(err)
    }
)

export default ax