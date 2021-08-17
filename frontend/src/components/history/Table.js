import React from 'react'
import {makeStyles} from '@material-ui/core/styles';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import ListSubheader from '@material-ui/core/ListSubheader';



const Table = (props) => {
    const {data, width} = props
    let {relatedMatches} = data
    relatedMatches = Array.from(new Set([...relatedMatches]))
    //13: {title: "Superbet Classic 2021 2021.06.08", playerA: "Vachier Lagrave,M", playerB: "Lupulescu,C"}
    const useStyles = makeStyles((theme) => ({
        container: {
            width: width,
            paddingTop: 10
        },
        root: {
            margin:5,
            width: '100%',
            maxWidth: width,
            backgroundColor: 'white',
            position: 'relative',
            overflow: 'auto',
            maxHeight: 300,
        },
        subheader:{
            backgroundColor:'white'
        },
        listSection: {
            backgroundColor: 'inherit',
        },
        ul: {
            backgroundColor: 'inherit',
            padding: 0,
        },
    }));
    const classes = useStyles()
    return (
            <List className={classes.root} subheader={<li/>}>
                <li key={`header`} >
                    <ul className={classes.ul}>
                        <ListSubheader className={classes.subheader}>{`This board state occurred in...`}</ListSubheader>
                        {relatedMatches.map((item, i) => (
                            <ListItem key={`item-${i}`}>
                                <ListItemText primary={`${item.title}: ${item.playerA} vs ${item.playerB}` }/>
                            </ListItem>
                        ))}
                    </ul>
                </li>
            </List>
    )

}
export default Table