import { Route, Routes } from "react-router-dom";
import { CustomerPage } from "./modules/customer/CustomerPage";
import { StaffPage } from "./modules/staff/StaffPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<CustomerPage />} />
      <Route path="/staff" element={<StaffPage />} />
    </Routes>
  );
}
