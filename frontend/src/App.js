import React from 'react'
import ResizeListener from "./components/resizeListener/ResizeListener";
import Board from "./components/board/Board";

function App() {
    return (
        <div>
            <ResizeListener>
                {({width, height}) => {
                    let primary = Math.min(width, height)
                    primary = Math.max(primary, 400)
                    const remainder = primary-(primary%8)
                    return <Board width={remainder} height={remainder}/>
                }}
            </ResizeListener>
        </div>
    );
}

export default App;
