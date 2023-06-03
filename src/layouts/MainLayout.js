import { AppBar, Box, Container, Toolbar, Typography } from '@mui/material'
import { Outlet } from "react-router-dom";
import React from 'react'

const MainLayout = () => {
  return (
    <Box mt={10}>
        <AppBar position="fixed">
            <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                Todo App
            </Typography>
            </Toolbar>
        </AppBar>
        <Container>
            <Outlet />
        </Container>
      </Box>
  )
}

export default MainLayout;