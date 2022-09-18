exports.inputData = (req, res) => {
    const body = req.body
    res.json({
        data: body
    })
}