import React from 'react'
import ResizeListener from "./components/resizeListener/ResizeListener";
import Board from "./components/board/Board";
import Table from './components/history/Table'
import Moves from './components/moves/Moves'
import Paper from '@material-ui/core/Paper';
import {makeStyles, TextField, Tooltip} from "@material-ui/core";
import IconButton from '@material-ui/core/IconButton';
import RotateLeftIcon from '@material-ui/icons/RotateLeft';
import axios from "axios";
import {parseFENToPieceSet} from "./components/board/Utils";
import * as pieces from "./components/board/pieces"


const useStyles = makeStyles(theme => ({
    paper: {
        margin: 5,
        paddingBottom: 5
    },
    board: {
        maxWidth: '60vw',
        display: 'flex',
        flexGrow: 1
    },
    centering: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        paddingTop: 100
    },
    buttonContainer: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: 5
    }
}))

const getData = async (fen) => {
//https://comp-chess-viz.azurewebsites.net/CCV?state=rnbqkbnr%2Fpppppppp%2F8%2F8%2F8%2F8%2FPPPPPPPP%2FRNBQKBNR+w+KQkq+-

    const config = {
        headers: {
            'Content-Type': 'application/json;charset=UTF-8',
            // "Access-Control-Allow-Origin": "*",
        },
        params: {state: fen}
    }
    let res = null
    try {
        res = await axios.get('https://comp-chess-viz.azurewebsites.net/CCV', config);
    } catch (err) {
        res = {data: {recommendedMoves: [], relatedMatches: []}}
    }
    return res.data

}

const reduceFen = (fen) => {
    return fen.split(' ').slice(0, 4).join(' ')
}


function App() {
    const classes = useStyles()
    const default_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    const [value, setValue] = React.useState(default_fen);
    const [stack, setStack] = React.useState([{move: '...', fen: default_fen}])//push the piece position and corresponding fen here
    const [data, setData] = React.useState(null)

    //gotta slice the fen to match

    React.useEffect(() => {
        const call = async () => {
            const data = await getData(reduceFen(value))
            setData(data)
        }
        call()
    }, [value]) //on value change recall the api call

    if (!data) {
        return null
    }

    const setFENandStack = (event) => {
        if (event.target.value === '') {
            setValue(default_fen)
            setStack([{move: '...', fen: default_fen}])
            return;
        }
        try {
            const test = parseFENToPieceSet(event.target.value)
            //also need to check if any of the pieces don't exist in our inputs
            const set = Object.keys(test).map(a => test[a])
            set.forEach(piece => {
                    if (!(piece in pieces)) {
                        throw 'Invalid FEN notation'
                    }
                }
            )
            setValue(event.target.value);
            setStack([{move: '...', fen: event.target.value}])
        } catch (error) {
            alert('Caught invalid FEN Code')
        }


    }

    const addToMoveStack = (move) => {
        //this will need to take the endPos and the fen of the state in that move, start by pushing the original
        setStack([...stack, move])
    }
    const popFromStack = (move) => {
        const index = stack.findIndex(a => a.move === move.move && a.fen === move.fen)
        if (index !== -1) {
            setStack([...stack.slice(0, index + 1)])
            setValue(move.fen)
        }
    }


    return (
        <div>
            <div>

            </div>
            <div className={classes.centering}>
                <div style={{display: 'flex', flexGrow: 0}}>

                </div>
                <div className={classes.board}>
                    <ResizeListener>
                        {({width, height}) => {
                            let primary = Math.min(width, height)
                            primary = primary > 800 ? 800 : primary < 400 ? 400 : primary
                            const remainder = primary - (primary % 8)
                            return (
                                <div>
                                    <Paper className={classes.paper} elevation={4}>
                                        <div style={{
                                            width: width,
                                            margin: 5,
                                            paddingTop: 5,
                                            display: 'flex',
                                            flexDirection: 'row'
                                        }}>
                                            <TextField
                                                id="standard"
                                                label="FEN Code"
                                                defaultValue={value}
                                                variant="outlined"
                                                onChange={setFENandStack}
                                                fullWidth
                                                value={value}
                                            />

                                            <div className={classes.buttonContainer}>
                                                <Tooltip title={'Reset to starting position'} placement={'top'}>
                                                    <IconButton color="primary" aria-label="upload picture"
                                                                component="span"
                                                                onClick={() => setValue(default_fen)}>
                                                        <RotateLeftIcon/>
                                                    </IconButton>
                                                </Tooltip>
                                            </div>
                                        </div>
                                        <Moves stack={stack} pop={popFromStack}/>
                                        <Board width={remainder} height={remainder} fen={value} data={data}
                                               updateFen={setValue} addMove={addToMoveStack}/>
                                        <Table data={data} width={width}/>
                                    </Paper>
                                </div>)
                        }}
                    </ResizeListener>
                </div>
            </div>
        </div>
    );
}

export default App;
