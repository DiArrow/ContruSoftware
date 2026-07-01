import { useState } from 'react';
import SemestreList from './SemestreList';
import SemestreForm from './SemestreForm';
import { useAuth } from '../context/AuthContext';

export default function SemestresPage() {
    const { currentUser } = useAuth();
    const [refreshTrigger, setRefreshTrigger] = useState(0);
    const puedeCrear = currentUser && ['ADM', 'AYU'].includes(currentUser.rol);

    const handleCreated = () => {
        setRefreshTrigger((prev) => prev + 1);
    };

    return (
        <div className="container mt-4">
            <h1 className="mb-4">Gestión de Semestres Académicos</h1>
            <div className="row">
                {puedeCrear && (
                    <div className="col-md-4">
                        <SemestreForm onCreated={handleCreated} />
                    </div>
                )}
                <div className={puedeCrear ? 'col-md-8' : 'col-md-12'}>
                    <div className="card p-3">
                        <h3>Lista de Semestres</h3>
                        <SemestreList refreshTrigger={refreshTrigger} />
                    </div>
                </div>
            </div>
        </div>
    );
}
