let proxySettings = null;

if (process.env.API_SERVER) {
    let server = {
        target: process.env.API_SERVER,
        secure: false,
    };

    proxySettings = {
        "/admin": server,
        "/auth": server,
        "/api": server,
        "/static": server,
    };
}

module.exports = {
    devServer: {
        proxy: proxySettings,
    }
};