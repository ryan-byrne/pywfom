import {useState, useEffect} from 'react';

import Modal from 'react-bootstrap/Modal';
import Alert from 'react-bootstrap/Alert';
import Table from 'react-bootstrap/Table';
import Spinner from 'react-bootstrap/Spinner';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import ButtonGroup from 'react-bootstrap/ButtonGroup';

export default function Edit(props){

  const [foundCameras, setFoundCameras] = useState([]);
  const [isSearching, setSearching] = useState(false);

  const searchCameras = (event) => {
    setSearching(true);
    fetch('/api/find/cameras')
      .then(resp => resp.json()
      .then(data => {
        setFoundCameras(data);
        setSearching(false);
        event.target.innerText = "Refresh";
      }))
  }

  const addCamera = (event, idx) => {
    event.target.textContent = 'Adding...';
    event.target.disabled = true;
    let cameras = [...foundCameras];
    const camera = cameras.shift(idx)
    console.log(idx, camera);
    // Send Message to API
    fetch('/api/connection/camera', {
      method: "POST",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(camera)})
      .then(resp => resp.json()
      .then(data => {
        props.setCurrentCameras([...props.currentCameras, camera])
        event.target.textContent = 'Add';
        event.target.disabled = false;
        setFoundCameras(cameras)
      })
    )
  }

  const removeCamera = (idx) => {
    //Send Message to API
    fetch('/api/close/'+idx.toString(), {method: "POST"})
    .then(resp => resp.json()
    .then(data => {
      let cameras = [...props.currentCameras];
      setFoundCameras([...foundCameras, cameras.shift(idx)])
      props.setCurrentCameras(cameras)
    }))
  }

  const searchingScreen = (
    <Alert variant='primary'>
      <Spinner size='sm' animation='border'/>  Searching for Cameras...
    </Alert>
  )

  const foundTable = (
        <Table className='text-center'>
          <tbody>
            <tr><th></th><th>Interface</th><th>Index</th></tr>
            {
              foundCameras.map((cam, idx) => {
                return(
                  <tr key={idx}>
                    <td><Button onClick={(e)=>addCamera(e,idx)}>Add</Button></td>
                    <td>{cam.interface}</td>
                    <td>{cam.index}</td>
                  </tr>
                )
              })
            }
          </tbody>
        </Table>
  )

  return(
    <Modal show={props.show} onHide={props.handleAdd}>
      <Modal.Header closeButton>
      </Modal.Header>
      <Modal.Body>
        <Modal.Title className='mb-3'>
          Available Cameras
          <Button onClick={!isSearching ? searchCameras : null} disabled={isSearching}
            className='ml-3' size='md'>
            {isSearching ? "Searching..." : "Search" }
          </Button>
        </Modal.Title>
        { isSearching ? searchingScreen : foundTable}
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
