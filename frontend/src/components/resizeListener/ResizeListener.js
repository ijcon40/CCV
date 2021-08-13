import React from 'react'

const ResizeListener = (props) => {
    const {children} = props
    const ref = React.createRef()
    const [width, setWidth] = React.useState(null)
    const [height, setHeight] = React.useState(null)
    React.useEffect(() => {
        if (!width && !height) {
            const element = ref.current
            setWidth(element.clientWidth)
            setHeight(element.clientHeight)
        }

        function handleResize() {
            const element = ref.current
            setWidth(element.clientWidth)
            setHeight(element.clientHeight)

        }

        window.addEventListener('resize', handleResize)
        return () => window.removeEventListener('resize', handleResize)
    }, [height, ref, width])

    return (
        <div ref={ref} style={{height: '100%'}}>{children({width, height})}< /div>
    )

}

export default ResizeListener
