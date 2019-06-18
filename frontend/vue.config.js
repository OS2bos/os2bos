let proxySettings = null;

if (process.env.API_SERVER) {
    let server = {
        target: process.env.API_SERVER,
        secure: false,
    };

    proxySettings = {
        "/api": server,
    };
}

module.exports = {
    devServer: {
        proxy: proxySettings,
    }
};
