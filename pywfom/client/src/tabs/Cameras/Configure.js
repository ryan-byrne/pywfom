import {useRef,useEffect,useState} from 'react';

import Modal from 'react-bootstrap/Modal';
import Image from 'react-bootstrap/Image';
import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import Button from 'react-bootstrap/Button';
import Tooltip from 'react-bootstrap/Tooltip';
import InputGroup from 'react-bootstrap/InputGroup';
import FormControl from 'react-bootstrap/FormControl';
import Tabs from 'react-bootstrap/Tabs';
import Tab from 'react-bootstrap/Tab';
import Form from 'react-bootstrap/Form';

const ImageDraw = (props) => {

  const [coor, setCoor] = useState({draw:false,x:0,y:0,ix:0,iy:0})
  const [margins, setMargins] = useState({})
  const [tooltip, setTooltip] = useState(null);

  const canvasRef = useRef();
  const imageRef = useRef();
  const containerRef = useRef();

  const handleUp = (event) => {
    const { height, naturalHeight, width } = imageRef.current;
    const { x, y, iy, ix } = coor;
    const scale = height/naturalHeight;
    const size = {
      x:Math.min(x,ix),
      y:Math.min(y,iy),
      height:Math.abs(y-iy),
      width:Math.abs(x-ix)
    }
    props.setCamera({...props.camera, aoi:{
      x:size.x/scale,y:size.y,height:size.height/scale,width:size.width/scale
    }})
    setCoor({draw:false,x:0,y:0,ix:0,iy:0})
  }

  const handleDown = (event) => {
    const { left, top} =  canvasRef.current.getBoundingClientRect()
    const { clientX, clientY } = event;
    setCoor({...coor, ix:clientX-left, iy:clientY-top, draw:true})
  }

  const handleMove = (event) => {
    const { left, top} =  canvasRef.current.getBoundingClientRect()
    const { clientX, clientY } = event;
    if (coor.draw) {
      const { ix, iy } = coor;
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
        ref={canvasRef} onMouseDown={handleDown} onMouseUp={handleUp} onMouseMove={handleMove}/>
      <Image ref={imageRef} src={props.camera?props.camera.feed:null} fluid draggable={false}/>
    </div>
  )
}

export default function ConfigureCamera(props) {

  const [camera, setCamera] = useState(props.camera)

  const handleSave = () => console.log(camera);

  const handleChange = (event, key) => setCamera({...camera, [key]:event.target.value})

  const handleSwitch = (event, key) => {
    if (key === "primary") {
      setCamera({...camera, [key]:event.target.checked})
    }
    else {
      setCamera({...camera, aoi:{...camera.aoi, [key]:event.target.checked}})
    }
  }

  const handleSelect = (event, key) => {
    if (key === 'binning') {
      setCamera({...camera, aoi:{...camera.aoi, binning:event.target.value}})
    } else {
      setCamera({...camera, dtype:event.target.value})
    }
  }

  const handleAoi = (event, key) => setCamera({...camera, aoi:{...camera.aoi, [key]:event.target.value}})

  return (
    <div>{ !camera ? null :
    <Modal show={props.configuring === null ? false : true}
      onHide={props.closeConfigure} size='xl'>
      <Modal.Header>
        <Modal.Title>
          Configuring Camera
        </Modal.Title>
      </Modal.Header>
      <Modal.Body className='text-center'>
        <ImageDraw camera={camera} setCamera={setCamera}/>
          <Tabs className='mt-3 mb-3'>
            <Tab eventKey="aoi" title="AOI">
              <Container className='h-100'>
                <Row className='h-100 align-items-center justify-content-center' xs="auto">
                  <Col xs="auto">
                    <InputGroup.Prepend>
                      <InputGroup.Text>Binning</InputGroup.Text>
                      <Form.Control as="select" className="text-center" custom
                        onChange={(e)=>handleSelect(e,"binning")} value={camera.aoi.binning}>
                        {
                          ['1x1','2x2','4x4','8x8'].map((bin, idx) => {
                            return(
                              <option key={idx}>{bin}</option>
                            )
                          })
                        }
                      </Form.Control>
                    </InputGroup.Prepend>
                  </Col>
                  <Col xs="auto">
                    <Form.Check type="switch" label="Centered" id="centered-switch"
                      onChange={(e)=>handleSwitch(e,"centered")}/>
                  </Col>
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
                            <FormControl onChange={(e)=>handleAoi(e,key)}
                              value={camera.aoi[key]} type="number" min={0} step={1}>
                            </FormControl>
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
                          disabled={!camera.primary} type='number' step={0.01} min={1}>
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
                          <Form.Control custom as='select' onChange={(e)=>handleSelect(e,'dtype')}>
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
      <Modal.Footer>
        <Button variant="secondary" onClick={props.closeConfigure}>Close</Button>
        <Button onClick={handleSave}>Save Changes</Button>
      </Modal.Footer>
    </Modal>
    }</div>
  )
}
