"""
SPARK — Base Repository
Provides shared Firestore utilities inherited by all repositories.
"""

from typing import Any, Optional, TypeVar

from google.cloud.firestore_v1.base_query import FieldFilter

from app.core.exceptions import DatabaseError, NotFoundError
from app.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class BaseRepository:
    """
    Base class for all Firestore repositories.
    Provides common read/write/delete operations.
    """

    def __init__(self) -> None:
        self._db = None

    def _get_db(self):
        if self._db is None:
            from app.core.firebase import get_firestore
            self._db = get_firestore()
        return self._db

    def _collection(self, path: str):
        return self._get_db().collection(path)

    def _document(self, collection: str, doc_id: str):
        return self._get_db().collection(collection).document(doc_id)

    def _get_document(
        self,
        collection: str,
        doc_id: str,
        resource_name: str = "Document",
    ) -> dict:
        try:
            doc_ref = self._document(collection, doc_id)
            doc = doc_ref.get()

            if not doc.exists:
                raise NotFoundError(resource_name, doc_id)

            data = doc.to_dict() or {}
            data["id"] = doc.id
            return data

        except NotFoundError:
            raise
        except Exception as exc:
            logger.error(
                "Firestore get failed",
                collection=collection,
                doc_id=doc_id,
                error=str(exc),
            )
            raise DatabaseError(f"Failed to get {resource_name}: {exc}") from exc

    def _set_document(
        self,
        collection: str,
        doc_id: str,
        data: dict,
        merge: bool = False,
    ) -> None:
        try:
            doc_ref = self._document(collection, doc_id)
            doc_ref.set(data, merge=merge)
        except Exception as exc:
            logger.error(
                "Firestore set failed",
                collection=collection,
                doc_id=doc_id,
                error=str(exc),
            )
            raise DatabaseError(f"Failed to save document: {exc}") from exc

    def _update_document(
        self,
        collection: str,
        doc_id: str,
        updates: dict,
    ) -> None:
        try:
            doc_ref = self._document(collection, doc_id)
            doc_ref.update(updates)
        except Exception as exc:
            logger.error(
                "Firestore update failed",
                collection=collection,
                doc_id=doc_id,
                error=str(exc),
            )
            raise DatabaseError(f"Failed to update document: {exc}") from exc

    def _delete_document(
        self,
        collection: str,
        doc_id: str,
    ) -> None:
        try:
            self._document(collection, doc_id).delete()
        except Exception as exc:
            logger.error(
                "Firestore delete failed",
                collection=collection,
                doc_id=doc_id,
                error=str(exc),
            )
            raise DatabaseError(f"Failed to delete document: {exc}") from exc

    def _query_collection(
        self,
        collection: str,
        filters: list[tuple],
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        descending: bool = False,
    ) -> list[dict]:
        """
        Queries a collection with filters.
        Uses FieldFilter keyword argument to avoid deprecation warning.

        Args:
            collection: Firestore collection path
            filters: List of (field, operator, value) tuples
            order_by: Field name to sort by
            limit: Maximum documents to return
            descending: Sort direction
        """
        try:
            query = self._collection(collection)

            # Use FieldFilter to avoid positional argument deprecation warning
            for field, operator, value in filters:
                query = query.where(filter=FieldFilter(field, operator, value))

            if order_by:
                from google.cloud.firestore_v1 import query as firestore_query
                direction = (
                    firestore_query.Query.DESCENDING
                    if descending
                    else firestore_query.Query.ASCENDING
                )
                query = query.order_by(order_by, direction=direction)

            if limit:
                query = query.limit(limit)

            docs = query.stream()
            results = []
            for doc in docs:
                data = doc.to_dict() or {}
                data["id"] = doc.id
                results.append(data)

            return results

        except Exception as exc:
            logger.error(
                "Firestore query failed",
                collection=collection,
                filters=str(filters),
                error=str(exc),
            )
            raise DatabaseError(f"Failed to query collection: {exc}") from exc

    def _batch_set(
        self,
        operations: list[tuple[str, str, dict]],
    ) -> None:
        try:
            db = self._get_db()
            batch = db.batch()

            for collection, doc_id, data in operations:
                doc_ref = db.collection(collection).document(doc_id)
                batch.set(doc_ref, data)

            batch.commit()

        except Exception as exc:
            logger.error("Firestore batch write failed", error=str(exc))
            raise DatabaseError(f"Batch write failed: {exc}") from exc

    def _subcollection_query(
        self,
        parent_collection: str,
        parent_id: str,
        subcollection: str,
        filters: Optional[list[tuple]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        descending: bool = False,
    ) -> list[dict]:
        """
        Queries a Firestore sub-collection.
        Uses FieldFilter keyword argument to avoid deprecation warning.
        """
        try:
            db = self._get_db()
            query = (
                db.collection(parent_collection)
                .document(parent_id)
                .collection(subcollection)
            )

            if filters:
                for field, operator, value in filters:
                    query = query.where(
                        filter=FieldFilter(field, operator, value)
                    )

            if order_by:
                from google.cloud.firestore_v1 import query as firestore_query
                direction = (
                    firestore_query.Query.DESCENDING
                    if descending
                    else firestore_query.Query.ASCENDING
                )
                query = query.order_by(order_by, direction=direction)

            if limit:
                query = query.limit(limit)

            docs = query.stream()
            results = []
            for doc in docs:
                data = doc.to_dict() or {}
                data["id"] = doc.id
                results.append(data)

            return results

        except Exception as exc:
            logger.error(
                "Firestore subcollection query failed",
                parent=f"{parent_collection}/{parent_id}",
                subcollection=subcollection,
                error=str(exc),
            )
            raise DatabaseError(f"Subcollection query failed: {exc}") from exc