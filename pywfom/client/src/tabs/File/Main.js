import {useEffect} from 'react';

import Form from 'react-bootstrap/Form';
import InputGroup from 'react-bootstrap/InputGroup';
import Container from 'react-bootstrap/Container';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import Button from 'react-bootstrap/Button';
import Dropdown from 'react-bootstrap/Dropdown';
import DropdownButton from 'react-bootstrap/DropdownButton';

export default function File(props){

  const handleUpdate = (event) => {
    props.setFileConfig({...props.fileConfig, [event.target.id]: event.target.value});
  }

  useEffect(() => {
    fetch('/api/configure/file')
      .then(res => res.json()
      .then(data => {
        props.setFileConfig({...props.fileConfig, directory:data.directory})
      }))
  },[])

  return (
    <Container fluid="sm">
      <InputGroup className="m-3">
        <Form.Control id="uni" type="text" placeholder="Enter UNI" onChange={handleUpdate}/>
        <Form.Control id="mouse" className="ml-3" type="text"
          onChange={handleUpdate} placeholder="Mouse ID" />
      </InputGroup>
      <InputGroup className="m-3">
        <Form.Control onChange={handleUpdate} id="run_length" type="number"
          placeholder="Run Length" min="0" step="0.01"/>
        <Form.Control onChange={handleUpdate} id="run_length_unit"
          className="mr-5 text-left w-3" as="select">
          <option></option>
          <option>Sec</option>
          <option>Min</option>
          <option>Hr</option>
        </Form.Control>
        <Form.Control onChange={handleUpdate} id="number_of_runs" className="ml-3"
          placeholder="Number of Runs"/>
      </InputGroup>
      <InputGroup className="m-3">
        <Form.Control className='text-center' type="text" id="directory" disabled
          placeholder={"Saving Files to "+props.fileConfig.directory}>
        </Form.Control>
      </InputGroup>
        <ButtonGroup className="float-right">
          <Button variant="danger" className='ml-1'>Close</Button>
          <DropdownButton variant="secondary" className='ml-1' as={ButtonGroup}
            title="File">
            <Dropdown.Item eventKey="1">Save Configuration</Dropdown.Item>
            <Dropdown.Item eventKey="2">Load Configuration</Dropdown.Item>
            <Dropdown.Item eventKey="3">Set to Default</Dropdown.Item>
            <Dropdown.Item eventKey="4">Make Default</Dropdown.Item>
          </DropdownButton>
          <Button className='ml-1'>Start Acquisition</Button>
        </ButtonGroup>

    </Container>
  )
}
