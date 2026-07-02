/**
 * SPARK — Root Application Component
 */

import React from "react";
import { BrowserRouter } from "react-router-dom";
import { QueryProvider } from "./providers/QueryProvider";
import { AuthProvider } from "./providers/AuthProvider";
import { Router } from "./Router";
import { ToastContainer } from "@shared/components/ui/Toast";

const App: React.FC = () => (
  <BrowserRouter>
    <QueryProvider>
      <AuthProvider>
        <Router />
        <ToastContainer />
      </AuthProvider>
    </QueryProvider>
  </BrowserRouter>
);

export default App;