import React from 'react'
import ResizeListener from "./components/resizeListener/ResizeListener";
import Board from "./components/board/Board";
import Paper from '@material-ui/core/Paper';
import {makeStyles, TextField} from "@material-ui/core";
import axios from "axios";

const useStyles = makeStyles(theme => ({
    paper: {
        margin: 5,
        paddingBottom: 5
    },
    board: {
        maxWidth: '40vw',
        display: 'flex',
        flexGrow: 1
    },
    centering: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        paddingTop: 100
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

    const res = await axios.get('https://comp-chess-viz.azurewebsites.net/CCV', config);
    return res.data

}

const reduceFen = (fen) => {
    return fen.split(' ').slice(0, 4).join(' ')
}


function App() {
    const classes = useStyles()
    const default_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    const [value, setValue] = React.useState(default_fen);
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

    const handleChange = (event) => {
        if (event.target.value === '') {
            setValue(default_fen)
            return;
        }
        setValue(event.target.value);
    };
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
                                        <div style={{width: width, margin: 5, paddingTop: 5}}>
                                            <TextField
                                                id="standard"
                                                label="FEN Code"
                                                defaultValue={value}
                                                variant="outlined"
                                                onChange={handleChange}
                                                fullWidth
                                            />
                                        </div>
                                        <Board width={remainder} height={remainder} fen={value} data={data} updateFen={setValue}/>
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
