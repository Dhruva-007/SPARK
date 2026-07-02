/**
 * SPARK — Task Zustand Store
 * Holds selected task and active task state.
 * Task lists are managed by React Query, not Zustand.
 * Zustand only holds UI-level task state.
 */

import { create } from "zustand";
import type { Task } from "@shared/types/task.types";

interface TaskStore {
  // The task currently being viewed/edited
  selectedTaskId: string | null;
  setSelectedTaskId: (id: string | null) => void;

  // The task currently in focus for the momentum engine
  focusedTaskId: string | null;
  setFocusedTaskId: (id: string | null) => void;

  // Create task modal
  createTaskModalOpen: boolean;
  openCreateTaskModal: () => void;
  closeCreateTaskModal: () => void;

  // Optimistic updates cache (task_id → partial Task)
  // Used to show immediate UI feedback before API confirms
  optimisticUpdates: Record<string, Partial<Task>>;
  applyOptimisticUpdate: (taskId: string, update: Partial<Task>) => void;
  clearOptimisticUpdate: (taskId: string) => void;
}

export const useTaskStore = create<TaskStore>((set) => ({
  selectedTaskId: null,
  setSelectedTaskId: (id) => set({ selectedTaskId: id }),

  focusedTaskId: null,
  setFocusedTaskId: (id) => set({ focusedTaskId: id }),

  createTaskModalOpen: false,
  openCreateTaskModal: () => set({ createTaskModalOpen: true }),
  closeCreateTaskModal: () => set({ createTaskModalOpen: false }),

  optimisticUpdates: {},
  applyOptimisticUpdate: (taskId, update) =>
    set((state) => ({
      optimisticUpdates: {
        ...state.optimisticUpdates,
        [taskId]: { ...(state.optimisticUpdates[taskId] || {}), ...update },
      },
    })),
  clearOptimisticUpdate: (taskId) =>
    set((state) => {
      const next = { ...state.optimisticUpdates };
      delete next[taskId];
      return { optimisticUpdates: next };
    }),
}));