import React from 'react'
import * as pieces from './pieces'

const Piece = (props)=>{
    const {x, y, width, type} = props
    const Component = pieces[type]
    return (
        <g transform={`translate(${x} ${y})`}><Component/></g>
    )

}

export default Piece