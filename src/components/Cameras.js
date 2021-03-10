import {useRef, useState,useEffect} from 'react';

import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import Spinner from 'react-bootstrap/Spinner';
import Alert from 'react-bootstrap/Alert';
import Table from 'react-bootstrap/Table';
import Image from 'react-bootstrap/Image';
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

const EditCameras = (props) => {

  const [foundCameras, setFoundCameras] = useState([]);

  const addCamera = (event, idx) => {
    event.target.textContent = 'Adding...';
    let cameras = [...foundCameras];
    const camera = cameras.pop(idx)
    // Send Message to API
    fetch('/connect/camera/', {
      method: "POST",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(camera)})
      .then(resp => resp.json()
      .then(data => {
        props.setCurrentCameras([...props.currentCameras, camera])
        setFoundCameras(cameras)
      })
    )
  }

  const removeCamera = (idx) => {
    //Send Message to API
    fetch('/close/camera/'+idx.toString(), {method: "POST"})
    .then(resp => resp.json()
    .then(data => {
      let cameras = [...props.currentCameras];
      setFoundCameras([...foundCameras, cameras.pop(idx)])
      props.setCurrentCameras(cameras)
    }))
  }

  useEffect(() => {
    fetch('/find/cameras')
      .then(resp=> resp.json()
      .then(data => setFoundCameras(data)))
  },[])

  // TODO: Set master camera

  return(
    <Modal show={props.show} onHide={props.handleAdd}>
      <Modal.Header closeButton>
      </Modal.Header>
      <Modal.Body>
        <Modal.Title>Available Cameras</Modal.Title>
        {foundCameras.length === 0 ?
          <Alert variant='info'>
            <Spinner animation='border' size='sm' className='mr-3'></Spinner>
              Searching for Cameras
          </Alert>
          :
            <Table>
              <tbody>
                <tr><th></th><th>Device</th><th>Index</th></tr>
                {foundCameras.map((cam,idx) => {
                  return(
                    <tr key={idx}>
                      <td><Button onClick={(e)=>addCamera(e, idx)}>Add</Button></td>
                      <td>{cam.device}</td>
                      <td>{cam.index}</td>
                    </tr>
                  )
                })}
              </tbody>
            </Table>
        }
        <Modal.Title>
          Current Cameras
        </Modal.Title>
        {
          props.currentCameras.length === 0 ?
          <Alert variant='warning'>No Cameras Added</Alert> :
          <Table>
            <tbody className='text-center'>
              <tr><th></th><th>Master</th><th>Name</th><th>Type</th><th>Index</th></tr>
              {props.currentCameras.map((cam,idx) => {
                return(
                  <tr key={idx}>
                    <td><Button onClick={()=>removeCamera(idx)}>Remove</Button></td>
                    <td><Form.Check/></td>
                    <td><Form.Control type="text"></Form.Control></td>
                    <td>{cam.device}</td>
                    <td>{cam.index}</td>
                  </tr>
                )
              })}
            </tbody>
          </Table>
        }
      </Modal.Body>
      <Modal.Footer>
        <Button onClick={props.handleAdd} variant="secondary">Close</Button>
        <Button variant="primary">Save changes</Button>
      </Modal.Footer>
    </Modal>
  )
}

const FakeCamera = (props) => {

  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, props.width, props.height);
    ctx.fillStyle = 'green';
    ctx.fillRect(0, 0, props.width, props.height);
  },[]);

  return (
    <canvas style={{border:'2px solid'}} height={canvasRef.height} width={canvasRef.width} ref={canvasRef}></canvas>
  )
}

export default function Cameras(){

  const [add, showAdd] = useState(false);
  const [cameras, setCameras] = useState([]);
  const [selected, setSelected] = useState(0);
  const handleAdd = (event) => showAdd(!add);

  const handleThumbnail = (event) => {

  }

  /*
  {
    !cameras[selected] ?
    <Alert variant='warning'>No Camera Selected</Alert> :
      <Image src={'/feed/'+selected.toString()} fluid></Image>
  }
  {
    cameras.length === 0 ? null :
    cameras.map((cam, idx) => {
      return(
        <Col><Image fluid src={'/feed/'+idx.toString()}></Image></Col>
      )
    })
  }
  */

  return (
    <Container className="text-center mt-3">
      <Row className='text-center col-md-3'><FakeCamera height={400} width={500} className='col-lg-3'/></Row>
      <Row>
      {
        [...Array(3).keys()].map((idx) => {
          return(
            <Col><FakeCamera className='float-left' height={50} width={50}/></Col>
          )
        })
      }
      </Row>
      <Button className="m-3" onClick={()=>showAdd(true)}>Edit Camera(s)</Button>
      <EditCameras show={add} handleAdd={handleAdd} currentCameras={cameras}
        setCurrentCameras={setCameras}/>
    </Container>
  )
}
