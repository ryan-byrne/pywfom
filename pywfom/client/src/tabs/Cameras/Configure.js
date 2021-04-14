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

  const [rect, setRect] = useState({draw:false,x:0,y:0,ix:0,iy:0});
  const [cropper, setCropper] = useState({overflow:"hidden", width:"100%"})
  const [image, setImage] = useState({width:"100%"})

  const canvasRef = useRef();
  const imageRef = useRef();
  const divRef = useRef();

  const handleUp = (event) => {
    if (event.button === 2){
      setCropper({...cropper, height:"100%",width:"100%"})
      setImage({width:"100%"})
      const {fullHeight, fullWidth} = props.camera.aoi
      props.setCamera({...props.camera,
        aoi:{...props.camera.aoi, x:0,y:0,height:fullHeight,width:fullWidth}})
    } else {
      // Get Rect Coordinates
      const {x,y,ix,iy} = rect;
      const aoi = {
        height:Math.abs(iy-y),
        width:Math.abs(ix-x),
        top:Math.min(iy,y),
        left:Math.min(ix,x)
      }
      // Set Size of Container
      setCropper({...cropper, width:aoi.width, height:aoi.height});
      // Get Size of Image
      const {naturalHeight, naturalWidth, height, width} = imageRef.current;
      const scale = naturalHeight/height;
      props.setCamera({...props.camera,
        aoi:{
          ...props.camera.aoi,
          x:parseInt(aoi.left*scale),
          y:parseInt(aoi.top*scale),
          width:parseInt(aoi.width*scale),
          height:parseInt(aoi.height*scale)
      }})
      // Set Viewing Image Frame
      setImage({...image, height:height, width:width,marginLeft:-aoi.left,marginTop:-aoi.top})

    }
    setRect({draw:false,x:0,y:0,ix:0,iy:0})
  }

  const handleDown = (event) => {
    const { left, top} =  canvasRef.current.getBoundingClientRect()
    const { clientX, clientY } = event;
    setRect({ix:clientX-left,iy:clientY-top,x:clientX-left,y:clientY-top,draw:true})
  }

  const handleMove = (event) => {
    const { left, top} =  canvasRef.current.getBoundingClientRect()
    const { clientX, clientY } = event;
    if (rect.draw) { setRect({...rect, x:clientX-left,y:clientY-top}) }
  }

  useEffect(()=>{
    let canvas = canvasRef.current;
    let ctx = canvas.getContext('2d');
    const { height, width } = imageRef.current;
    canvas.height = height;
    canvas.width = width;
    ctx.clearRect(0,0,canvas.width,canvas.height)
    ctx.strokeStyle = 'red';
    const { ix, iy, x, y } = rect;
    if (rect.draw) {ctx.strokeRect(ix,iy,x-ix,y-iy)}
  })

  return (
    <div onMouseDown={handleDown} onMouseMove={handleMove} onMouseUp={handleUp}
      style={cropper} ref={divRef}>
      <canvas ref={canvasRef} onContextMenu={(e)=>e.preventDefault()} className="position-absolute"/>
      <Image ref={imageRef} src={"/api/feed/"+props.camera.id} draggable={false} onContextMenu={(e)=>e.preventDefault()}
        style={image}/>
    </div>
  )
}

export default function ConfigureCamera(props) {

  // Store temprary viewing settings
  const [camera, setCamera] = useState(null);

  const handleSave = () => {
    fetch(`/api/system/settings/${props.selected}`,{
      method:"PUT",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(camera)
    })
      .then(resp=>{
        if(resp.ok){ resp.json().then(data=>{
          let cams = [...props.cameras]
          cams[props.selected] = camera;
          console.log(cams);
          props.setCameras(cams);
          props.onHide();
        })}
        else { resp.text().then(txt=>console.error(txt)) }
      })
  };

  const handleSwitch = (event) => {
    if (event.target.id === 'primary'){
      setCamera({...camera, primary:event.target.checked})
    } else {
      var newX; var newY;
      const {fullWidth, fullHeight, x, y, height, width} = camera.aoi;
      if( event.target.checked) {
        newX = (fullWidth-width)/2
        newY = (fullHeight-height)/2
      } else { newX=x; newY=y}
      setCamera({...camera, aoi:{...camera.aoi, centered:event.target.checked, x:newX, y:newY}})
    }
  }

  const handleSelect = (event) => {
    if (event.target.id === 'binning'){
      setCamera({...camera,aoi:{...camera.aoi, binning:event.target.value}})
    } else {
      setCamera({...camera, dtype:event.target.value})
    }
  }

  const handleNumber = (event) => {
    setCamera({...camera, aoi:{...camera.aoi,
      [event.target.id]:event.target.value
    }});
  }

  const calculateFrameSize = () => {}

  useEffect(()=> { setCamera(props.cameras[props.selected]) },[props])

  return (
    <div>{
    <Modal show={props.selected === null ? false : true}
      onHide={props.onHide} size='xl'>
      {
        <div>
        <Modal.Header closeButton>
          <Modal.Title>
            Configuring Camera
          </Modal.Title>
        </Modal.Header>
        { !camera ? null :
          <Modal.Body>
            <Row className="justify-content-center">
              <ImageDraw camera={camera} setCamera={setCamera}/>
            </Row>
            <Tabs className="mt-3">
              <Tab eventKey="aoiTab" title="AOI">
                <Container>
                  <Row className="justify-content-center mt-3 align-items-center" xs={1} sm={4}>
                    <InputGroup as={Col}>
                      <InputGroup.Text>Binning</InputGroup.Text>
                      <FormControl as="select" custom className="text-center"
                        value={camera.aoi.binning} onChange={handleSelect} id="binning">
                        {
                          ['1x1','2x2','4x4','8x8'].map(bin=><option key={bin}>{bin}</option>)
                        }
                      </FormControl>
                    </InputGroup>
                    <Col className="text-center">
                      <Form.Check type="switch" id="centered" label="Centered"
                        value={camera.aoi.centered} onChange={handleSwitch}>
                      </Form.Check>
                    </Col>
                  </Row>
                  <Row className="justify-content-center mt-3" xs={2} sm={6}>
                    {
                      ["height", "width", "x", "y"].map(setting => {
                        return (
                          <Form.Group as={Col} key={setting}>
                            <Form.Control type="number" min="0" step="1" className="text-center"
                              value={camera.aoi[setting]} id={setting} onChange={handleNumber}/>
                            <Form.Text muted>
                              {setting.charAt(0).toUpperCase()+setting.slice(1)}
                            </Form.Text>
                          </Form.Group>
                        )
                      })
                    }
                  </Row>
                </Container>
              </Tab>
              <Tab eventKey="framerateKey" title="Framerate">
                <Container className="mt-3">
                  <Form.Group as={Row} className="justify-content-center">
                    <Form.Check type="switch" label="Primary" value={camera.primary}
                        onChange={handleSwitch} id="primary"/>
                    </Form.Group>
                    <Form.Group as={Row} xs={4} className="justify-content-center">
                      <Form.Group>
                        <Form.Control type="number" min="0" step="0.01"
                          value={camera.framerate} disabled={camera.primary?false:true}
                          onChange={handleNumber}/>
                        <Form.Text muted>Framerate</Form.Text>
                      </Form.Group>
                    </Form.Group>
                </Container>
              </Tab>
              <Tab eventKey="pixelKey" title="Pixel Format">
                <Container className="mt-3">
                  <Form.Group as={Row} className="justify-content-center">
                    <Form.Group>
                      <Form.Control as="select" custom value={camera.dtype}
                          onChange={handleSelect}>
                          {['uint8','uint16','uint32'].map(bit=>{
                            return(<option key={bit}>{bit}</option>)
                          })}
                      </Form.Control>
                      <Form.Text muted>Bits Per Pixel</Form.Text>
                    </Form.Group>
                  </Form.Group>
                  <Form.Group as={Row} className="justify-content-center">
                    <Form.Group>
                      <InputGroup.Prepend>
                        <InputGroup.Text>{calculateFrameSize()}</InputGroup.Text>
                        <InputGroup.Text>MB</InputGroup.Text>
                      </InputGroup.Prepend>
                      <Form.Text muted>MB per Frame</Form.Text>
                    </Form.Group>
                  </Form.Group>
                </Container>
              </Tab>
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
