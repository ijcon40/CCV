import React from 'react'
import {makeStyles, rgbToHex, Typography} from "@material-ui/core";
import {parseFENToPieceSet} from "./Utils";
import Piece from "./Piece";
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';

const useStyles = makeStyles(theme => ({
    notification: {
        backgroundColor: '#B3E5FC',
        paddingLeft:5,
        paddingRight:5,
        paddingTop:10,
        paddingBottom:10,
        display: 'flex',
        flexDirection: 'row',
        alignItems:'center',
        width:'100%',
        margin:5
    }
}))

const LIGHT = rgbToHex('rgb(227,193,111)')
const DARK = rgbToHex('rgb(184,139,74)')
const SOURCE = rgbToHex('rgb(34,139,34)')
const HOVERED = rgbToHex('rgb(87,146,86)')
const POSSIBLE = rgbToHex('rgb(165, 159, 199)')


const Board = (props) => {
    const {width, height, fen, data, updateFen, addMove} = props
    const [selected, setSelected] = React.useState('')
    const {recommendedMoves} = data
    const classes = useStyles()
    const end_mapping = {}//take the data and reformat it to start-> {end:, fen:}
    //generate the end mapping for all moves
    recommendedMoves.forEach(a => {
        if (!(a.startPos in end_mapping)) {
            end_mapping[a.startPos] = []
        }
        end_mapping[a.startPos].push({end: a.endPos, fen: a.resultingFEN})
    })
    //endPos: "d4"
    // resultingFEN: "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq -"
    // startPos: "d2"

    const updateSelected = (uci) => {
        //check if the next one is in the end mapping
        if (!end_mapping[selected]) {
            setSelected(uci)
        }
        const ucis = end_mapping[selected]?.map(a => a.end)
        const has = ucis && ucis.length > 0 && ucis.indexOf(uci) !== -1
        if (has) {
            const _fen = end_mapping[selected].find(a => a.end === uci).fen
            updateFen(_fen)
            setSelected('')
            addMove({move:uci, fen:_fen})
        } else {
            setSelected(uci)//use this as the start for the start
        }

    }
    //make sure match the index


    const square = width / 8
    const FEN = fen
    const pieces = parseFENToPieceSet(FEN)
    const x = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    const y = [1, 2, 3, 4, 5, 6, 7, 8].reverse()//to make the white pieces at the bottom
    const hasMoves = !(end_mapping[selected]?.map(a => a.end).length === 0||recommendedMoves.length===0)

    return (
        <div style={{display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', margin: 5}}>
            <svg width={width} height={height} style={{backgroundColor: '#0fa000'}}>
                {y.reduce((a, c, y_ind) => {
                    return [...a, ...x.map((_x, x_ind) => {
                        const absolute_index = y_ind + x_ind
                        const isDark = (absolute_index % 2) === 1
                        let piece = null
                        if (pieces[_x + c]) {
                            piece = pieces[_x + c]
                        }
                        const square_label = _x + c
                        const hasMove = recommendedMoves.map(a => a.startPos).indexOf(square_label) !== -1
                        const show_label = (x_ind === 0 && c) || (y_ind === 7 && _x)
                        const start = square_label === selected
                        const target = end_mapping[selected] && end_mapping[selected].map(a => a.end).indexOf(square_label) !== -1
                        return (
                            <Square x={square * x_ind} y={square * y_ind}
                                    color={start ? SOURCE : hasMove ? POSSIBLE : isDark ? DARK : LIGHT} width={square}
                                    label={square_label} show_label={show_label} key={y_ind * 8 + x_ind} piece={piece}
                                    target={target} setClicked={updateSelected}/>)
                    })]
                }, [])}

            </svg>
            {!hasMoves && (
                <div className={classes.notification}>
                    <InfoOutlinedIcon/>
                    <Typography variant={'h6'} style={{paddingLeft:3}}>
                        No competitively played moves from this position
                    </Typography>
                </div>
            )}
        </div>
    )
}

const Square = (props) => {
    const {x, y, color, width, label, piece, target, setClicked, show_label} = props
    const centering = Math.max(0, (width - 45) / 2)
    return (
        <g onClick={() => {
            setClicked(label)
        }}>
            <rect x={x} y={y} width={width} height={width} fill={color}/>
            {show_label && <text x={x} y={y + width - 5}>{show_label}</text>}
            {piece && <Piece type={piece} x={centering + x} y={centering + y}/>}
            {target && <circle cx={x + width / 2} cy={y + width / 2} r={45 / 4} fill={HOVERED}/>}
        </g>
    )

}

export default Board