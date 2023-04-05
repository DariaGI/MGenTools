async function request({method, url, data}) {
    return await fetch(
        url, {
            method: method,
            body: data,

            cache: "no-cache",
        }
    )
    .then(response => response.text())
}