import {useRef,useEffect,useState} from 'react';

import Modal from 'react-bootstrap/Modal';
import Image from 'react-bootstrap/Image';
import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import Button from 'react-bootstrap/Button';
import InputGroup from 'react-bootstrap/InputGroup';
import FormControl from 'react-bootstrap/FormControl';
import Tabs from 'react-bootstrap/Tabs';
import Tab from 'react-bootstrap/Tab';
import Form from 'react-bootstrap/Form';

const ImageDraw = (props) => {

  const [coor, setCoor] = useState({draw:false,x:0,y:0,ix:0,iy:0})

  const canvasRef = useRef();
  const imageRef = useRef();
  const containerRef = useRef();

  const handleUp = (event) => {
    const { height, naturalHeight } = imageRef.current;
    const { x, y, iy, ix } = coor;
    const scale = height/naturalHeight;
    const size = {
      x:Math.min(x,ix),
      y:Math.min(y,iy),
      height:Math.abs(y-iy),
      width:Math.abs(x-ix)
    }
    props.setCamera({...props.camera, aoi:{
      ...props.camera.aoi,
      x:parseInt(size.x/scale),
      y:parseInt(size.y),
      height:parseInt(size.height/scale),
      width:parseInt(size.width/scale)
    }})
    setCoor({draw:false,x:0,y:0,ix:0,iy:0})
  }

  const handleDown = (event) => {
    if (event.button===2){
      const {fullWidth, fullHeight} = props.camera.aoi;
      console.log(fullHeight, fullWidth);
      props.setCamera(
        {...props.camera, aoi:{...props.camera.aoi, x:0, y:0, width:fullWidth, height:fullHeight}
      })
    } else {
      const { left, top} =  canvasRef.current.getBoundingClientRect()
      const { clientX, clientY } = event;
      setCoor({...coor,
        ix:clientX-left,
        iy:clientY-top,
        x:clientX-left,
        y:clientY-top,
        draw:true})
    }
  }

  const handleMove = (event) => {
    const { left, top} =  canvasRef.current.getBoundingClientRect()
    const { clientX, clientY } = event;
    if (coor.draw) {
      setCoor({...coor, x:clientX-left,y:clientY-top})
    } else {
    }
  }

  useEffect(()=>{
    let canvas = canvasRef.current;
    let ctx = canvas.getContext('2d');
    const { height, width } = imageRef.current;
    canvas.height = height;
    canvas.width = width;
    ctx.clearRect(0,0,canvas.width,canvas.height)
    ctx.strokeStyle = 'red';
    const { ix, iy, x, y } = coor;
    if (coor.draw) {ctx.strokeRect(ix,iy,x-ix,y-iy)}
  })

  const containerStyle = {
    position:'relative',
    overflow:'hidden'
  }

  return (
    <div ref={containerRef} style={containerStyle}>
      <canvas style={{cursor:'crosshair'}} className="position-absolute"
        ref={canvasRef} onMouseDown={handleDown} onMouseUp={handleUp} onMouseMove={handleMove}
        onContextMenu={(e)=>e.preventDefault()}/>
      <Image ref={imageRef} src={"/api/feed/"+props.camera.id} fluid draggable={false}/>
    </div>
  )
}

export default function ConfigureCamera(props) {

  // Store temprary viewing settings
  const [camera, setCamera] = useState({aoi:{binning:null}});

  const handleSave = () => console.log(camera);

  const handleChange = (event, key) => {}

  const handleSwitch = (event, key) => {}

  const handleSelect = (event, key) => {}

  const handleAoi = (event, key) => {}

  useEffect(() => {
    setCamera(props.cameras[props.selected])
  },[props.selected])

  return (
    <div>{
    <Modal show={props.selected === null ? false : true}
      onHide={props.onHide} size='xl'>
      {
        <div>
        <Modal.Header>
          <Modal.Title>
            Configuring Camera
          </Modal.Title>
        </Modal.Header>
        { !camera ? null :
        <Modal.Body className='text-center'>
          <ImageDraw camera={camera} setCamera={setCamera}/>
            <Tabs className='mt-3 mb-3'>
              <Tab eventKey="aoi" title="AOI">
                <Container className='h-100'>
                  <Row className='h-100 align-self-center justify-content-center' xs="auto">
                    <InputGroup>
                      <InputGroup.Prepend>
                        <InputGroup.Text>Binning</InputGroup.Text>
                      </InputGroup.Prepend>
                      <Col xs="auto">
                        <FormControl as="select" custom></FormControl>
                        <Form.Text muted>Horizontal</Form.Text>
                      </Col>
                      <div className='h-100 align-self-center'>X</div>
                      <Col xs="auto">
                        <FormControl as="select" custom></FormControl>
                        <Form.Text muted>Vertical</Form.Text>
                      </Col>
                      <Col xs="auto">
                        <Form.Check type="switch" label="Centered" id="centered-switch"
                          value={camera.aoi.centered} onChange={(e)=>handleSwitch(e,"centered")}/>
                      </Col>
                    </InputGroup>
                  </Row>
                  <Row className='mt-3 justify-content-center' sm={2} md={2} lg={4}>
                    {
                      ['x','y','width','height'].map((key,idx)=>{
                        return(
                          <Col key={idx}>
                            <InputGroup.Prepend>
                              <InputGroup.Text>
                                {key.charAt(0).toUpperCase()+key.slice(1)}:
                              </InputGroup.Text>
                              <Form.Control onChange={(e)=>handleAoi(e,key)}
                                value={camera.aoi[key]} type="number"
                                min={0} step={1}>
                              </Form.Control>
                            </InputGroup.Prepend>
                          </Col>
                        )
                      })
                    }
                  </Row>
                </Container>
              </Tab>
              <Tab eventKey="framerate" title="Framerate">
                <Container className='h-100'>
                  <Row className='h-100 align-items-center'>
                    <Col>
                      <Form.Check type="switch" id="primarySwitch" label="Primary"
                        className="mr-5" onChange={(e)=>handleSwitch(e, "primary")}>
                      </Form.Check>
                    </Col>
                    <Col>
                      <InputGroup>
                        <InputGroup.Prepend>
                          <FormControl onChange={(e)=>handleChange(e,"framerate")}
                            value={camera.framerate}
                            disabled={camera.primary?true:false} type='number' step={0.01} min={1}>
                          </FormControl>
                          <InputGroup.Text>FPS</InputGroup.Text>
                        </InputGroup.Prepend>
                      </InputGroup>
                    </Col>
                  </Row>
                </Container>
              </Tab>
              <Tab eventKey="pixel-format" title="Pixel Format">
                <Container className='h-100'>
                  <Row className='h-100 align-items-center text-center'>
                    <Col>
                      <InputGroup>
                        <InputGroup.Prepend>
                          <InputGroup.Text>Pixel Size</InputGroup.Text>
                            <Form.Control custom as='select' onChange={(e)=>handleSelect(e,'dtype')}
                              value={camera.dtype}>
                            {
                              ['8-bit','16-bit','32-bit'].map((bit, idx)=>{
                                return(
                                  <option key={idx}>{bit}</option>
                                )
                              })
                            }
                            </Form.Control>
                        </InputGroup.Prepend>
                      </InputGroup>
                    </Col>
                    <Col>
                      <InputGroup>
                        <InputGroup.Prepend>
                          <InputGroup.Text>Frame Size</InputGroup.Text>
                          <Form.Control as="text">Hello</Form.Control>
                        </InputGroup.Prepend>
                      </InputGroup>
                    </Col>
                  </Row>
                </Container>
              </Tab>
              <Tab eventKey="info" title="Info"></Tab>
            </Tabs>
        </Modal.Body>
        }
        <Modal.Footer>
          <Button variant="secondary" onClick={props.onHide}>Close</Button>
          <Button onClick={handleSave}>Save Changes</Button>
        </Modal.Footer>
      </div>}
    </Modal>
    }</div>
  )
}
