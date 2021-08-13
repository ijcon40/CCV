import React from 'react'
import {rgbToHex} from "@material-ui/core";
import {parseFENToPieceSet} from "./Utils";
import Piece from "./Piece";

const LIGHT = rgbToHex('rgb(227,193,111)')
const DARK = rgbToHex('rgb(184,139,74)')


const Board = (props) => {
    const {width, height, fen} = props
    const square = width / 8
    const FEN = fen
    const pieces = parseFENToPieceSet(FEN)
    const x = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    const y = [1, 2, 3, 4, 5, 6, 7, 8].reverse()//to make the white pieces at the bottom

    return (
        <div style={{display: 'flex', flexDirection: 'row', justifyContent: 'center', alignItems: 'center', margin:5}}>
            <svg width={width} height={height} style={{backgroundColor: '#0fa000'}}>
                {y.reduce((a, c, y_ind) => {
                    return [...a, ...x.map((_x, x_ind) => {
                        const absolute_index = y_ind + x_ind
                        const isDark = (absolute_index % 2) === 1
                        let piece = null
                        if(pieces[_x+c]){
                            piece = pieces[_x+c]
                        }
                        return (
                            <Square x={square * x_ind} y={square * y_ind} color={isDark ? DARK : LIGHT} width={square}
                                    label={(x_ind===0&&c)||(y_ind===7&&_x)} key={y_ind * 8 + x_ind} piece={piece}/>)
                    })]
                }, [])}

            </svg>
        </div>
    )
}

const Square = (props) => {
    const {x, y, color, width, label, piece} = props
    const centering = Math.max(0, (width-45)/2)
    return (
        <g>
            <rect x={x} y={y} width={width} height={width} fill={color}/>
            {label &&<text x={x} y={y+width-5}>{label}</text>}
            {piece &&<Piece type={piece} x={centering+x} y={centering+y}/>}
        </g>
    )

}

export default Board