import React, { useEffect, useState } from 'react'
import useTodos from '../../hooks/useTodos';
import { Button, Dialog, Stack, TextField } from '@mui/material';
import PATHS from '../../routes/path';
import { useNavigate } from 'react-router-dom';

const TodoDialog = ({ id }) => {
    const navigate = useNavigate();
    const [{ selectedTodo }, { getTodo, updateTodo }] = useTodos();
    const [task, setTask ] = useState(selectedTodo?.task)

    const handleCloseDialog = () => navigate(`${PATHS.todo.list}`, { replace: true });
    const handleSubmit = async (e) => {
        e.preventDefault()
        await updateTodo(selectedTodo.id, { task })
        handleCloseDialog()
    }
        

    useEffect(() => {
        if (id) {
            getTodo(id);
        }
    },[id]);

    useEffect(() => {
        if (selectedTodo)
            setTask(selectedTodo.task)
    },[selectedTodo]);
        
    
    if (!id) return null;
    if (!selectedTodo) return null;
    
  return (
    <Dialog open onClose={handleCloseDialog}>
        <Stack spacing={2} p={3} component='form' onSubmit={handleSubmit}>
            <TextField value={task} onChange={(e) => setTask(e.target.value)}  />
            <Button variant='outlined' type='submit'>Save</Button>
        </Stack>
    </Dialog> 
  )
}

export default TodoDialog