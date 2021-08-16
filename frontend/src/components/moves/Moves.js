import React from 'react'
import Breadcrumbs from '@material-ui/core/Breadcrumbs';
import Link from '@material-ui/core/Link';
import NavigateNextIcon from '@material-ui/icons/NavigateNext';
import {makeStyles} from "@material-ui/core/styles";

const useStyles = makeStyles(theme=>({
    wrapper:{
        paddingLeft:5
    }
}))

const Moves = (props) => {
    let {stack, pop} = props
    //take the last three from the stack
    const classes = useStyles()
    let ellipse = false
    if (stack.length > 3) {
        stack = stack.slice(stack.length - 3)
        ellipse=true
    }
    return (
        <div className={classes.wrapper}>
        <Breadcrumbs separator={<NavigateNextIcon fontSize="small"/>} aria-label="breadcrumb">
            {ellipse&&<Link color={"inherit"} >...</Link>}
            {stack.map(a => (<Link color={"inherit"} onClick={() => pop(a)}>{a.move}</Link>))}
        </Breadcrumbs>
        </div>
    )
}

export default Moves