'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { logout } from '@/lib/auth';
import {
  AdminUser,
  fetchAllUsers,
  verifyUser,
  revokeUser,
  reactivateUser,
  deleteUser,
} from '@/lib/api';

export default function AllUsersPage() {
  const router = useRouter();
  const [allUsers, setAllUsers] = useState<AdminUser[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);

  const loadUsers = useCallback(async () => {
    try {
      const users = await fetchAllUsers();
      setAllUsers(users);
      setError(null);
    } catch (err) {
      if (err instanceof Error && err.message.includes('403')) {
        router.push('/chat');
        return;
      }
      setError(err instanceof Error ? err.message : 'Failed to load users');
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  const handleAction = async (
    userId: number,
    action: 'verify' | 'revoke' | 'reactivate' | 'delete'
  ) => {
    setActionLoading(userId);
    setError(null);
    try {
      switch (action) {
        case 'verify':
          await verifyUser(userId);
          break;
        case 'revoke':
          await revokeUser(userId);
          break;
        case 'reactivate':
          await reactivateUser(userId);
          break;
        case 'delete':
          await deleteUser(userId);
          setDeleteConfirm(null);
          break;
      }
      await loadUsers();
    } catch (err) {
      if (err instanceof Error && err.message.includes('401')) {
        logout();
        router.push('/login');
        return;
      }
      setError(err instanceof Error ? err.message : `Failed to ${action} user`);
    } finally {
      setActionLoading(null);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl">
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        All Users ({allUsers.length})
      </h2>

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                Name
              </th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                Email
              </th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                Status
              </th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                Role
              </th>
              <th className="px-4 py-3 text-right text-sm font-semibold text-gray-900">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {allUsers.map((user) => (
              <tr key={user.id}>
                <td className="px-4 py-3 text-sm text-gray-900">
                  {user.full_name}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {user.email}
                </td>
                <td className="px-4 py-3">
                  {!user.is_verified ? (
                    <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800">
                      Pending
                    </span>
                  ) : !user.is_active ? (
                    <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800">
                      Deactivated
                    </span>
                  ) : (
                    <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                      Active
                    </span>
                  )}
                </td>
                <td className="px-4 py-3">
                  {user.is_admin ? (
                    <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800">
                      Admin
                    </span>
                  ) : (
                    <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">
                      User
                    </span>
                  )}
                </td>
                <td className="px-4 py-3 text-right">
                  <div className="flex justify-end gap-2">
                    {!user.is_verified && (
                      <button
                        onClick={() => handleAction(user.id, 'verify')}
                        disabled={actionLoading === user.id}
                        className="px-3 py-1 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 disabled:opacity-50"
                      >
                        Approve
                      </button>
                    )}
                    {user.is_verified && user.is_active && !user.is_admin && (
                      <button
                        onClick={() => handleAction(user.id, 'revoke')}
                        disabled={actionLoading === user.id}
                        className="px-3 py-1 bg-orange-100 text-orange-700 text-sm rounded-lg hover:bg-orange-200 disabled:opacity-50"
                      >
                        Revoke
                      </button>
                    )}
                    {!user.is_active && (
                      <button
                        onClick={() => handleAction(user.id, 'reactivate')}
                        disabled={actionLoading === user.id}
                        className="px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-lg hover:bg-blue-200 disabled:opacity-50"
                      >
                        Reactivate
                      </button>
                    )}
                    {!user.is_admin && (
                      deleteConfirm === user.id ? (
                        <>
                          <button
                            onClick={() => handleAction(user.id, 'delete')}
                            disabled={actionLoading === user.id}
                            className="px-3 py-1 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 disabled:opacity-50"
                          >
                            Confirm
                          </button>
                          <button
                            onClick={() => setDeleteConfirm(null)}
                            className="px-3 py-1 bg-gray-200 text-gray-700 text-sm rounded-lg hover:bg-gray-300"
                          >
                            Cancel
                          </button>
                        </>
                      ) : (
                        <button
                          onClick={() => setDeleteConfirm(user.id)}
                          className="px-3 py-1 bg-red-100 text-red-700 text-sm rounded-lg hover:bg-red-200"
                        >
                          Delete
                        </button>
                      )
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
