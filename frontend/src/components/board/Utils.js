

export const parseFENToPieceSet = (FEN)=>{
    //here we need to take a standard 8 row fen notation and create a hashset
    //rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
    //top down so the first row corresponds to 8
    const x = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    const representation = FEN.split(' ')[0]
    const rows = representation.split('/')
    const piece_dict = {}
    rows.forEach((a, row_index)=>{
        let index = 8-row_index //black starts at the top
        const moves = a.split('')
        let cross_index = 1
        moves.forEach(a=>{
            const test=Number(a)
            if(!Number.isNaN(test)){
                cross_index+=Number(a)
                return
            }
            //get the label using cross index
            const label = String(x[cross_index-1])+String(index)
            piece_dict[label]=a
            cross_index+=1
        })
    })
    return piece_dict

}